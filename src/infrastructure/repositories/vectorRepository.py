import io
import fitz
import base64
import pytesseract
from typing import Tuple, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchain_core.messages import HumanMessage
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI

from src.domain.interfaces.repositories.vectorRepository import IVectorRepository
from src.infrastructure.adapters.neighborRetriever import NeighborRetriever
from src.infrastructure.context.mongoContext import MongoContext


class VectorRepository(IVectorRepository):
    def __init__(
        self, 
        context: MongoContext, 
        collection_name: str, 
        index_name: str,
        chunk_size: int,
        chunk_overlap: int,
        model: str,
        azure_deployment: str,
        azure_endpoint: str,
        api_version: str,
        api_key: str
    ):
        self.context = context
        self.collection = context.get_collection(collection_name)
        self.index_name = index_name
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        self.embeddings = AzureOpenAIEmbeddings(
            model=model,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            api_key=api_key
        )

        self.llm = AzureChatOpenAI(
            azure_deployment=azure_deployment,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            api_key=api_key,
            temperature=1.0
        )


    def _process_image(self, img: Image.Image) -> dict:
        result = {"ocr": "", "description": ""}
        
        try:
            ocr_text = pytesseract.image_to_string(
                img.convert('L'), 
                lang='por+eng',
                config='--oem 3 --psm 6'
            ).strip()
            result["ocr"] = ocr_text

        except Exception:
            pass
        
        try:
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode()

            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Descreva esta imagem em uma frase simples e objetiva em português."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ]
            )

            response = self.llm.invoke([message])
            result["description"] = response.content

        except Exception:
            result["description"] = "Imagem não processada"
        
        return result

    def _process_images_parallel(self, images: List[Image.Image], max_workers: int = 5) -> List[dict]:
        if not images:
            return []
        
        results = [None] * len(images)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(self._process_image, img): idx 
                for idx, img in enumerate(images)
            }
            
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()

                except Exception:
                    results[idx] = {"ocr": "", "description": "Imagem não processada"}
        
        return results

    def _format_image_content(self, result: dict, index: int = None) -> str:
        parts = []
        
        prefix = f"[Imagem {index}]" if index else "[Imagem]"
        
        if result["description"]:
            parts.append(f"{prefix}: {result['description']}")
        
        if result["ocr"] and len(result["ocr"]) > 10:
            parts.append(f"[Texto na imagem: {result['ocr']}]")
        
        return "\n".join(parts) if parts else ""

    def _is_full_page_image(self, page, img_info) -> bool:
        try:
            page_rect = page.rect
            page_area = page_rect.width * page_rect.height
            
            xref = img_info[0]
            img_rects = page.get_image_rects(xref)
            
            if img_rects:
                img_area = img_rects[0].width * img_rects[0].height
                return (img_area / page_area) > 0.8
            
        except Exception:
            pass
        
        return False

    async def _extract_pdf_content(self, file_path: str) -> List[Document]:
        import asyncio
        loop = asyncio.get_event_loop()
        
        pdf_document = fitz.open(file_path)
        
        pages_data = []
        all_images = []
        image_map = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text().strip()
            images = page.get_images(full=True)
            
            page_info = {
                "page_num": page_num,
                "text": text,
                "has_text": len(text) > 100,
                "is_full_page_image": False,
                "image_results": []
            }
            
            if page_info["has_text"]:
                for img_info in images:
                    if self._is_full_page_image(page, img_info):
                        continue
                    try:
                        xref = img_info[0]
                        base_image = pdf_document.extract_image(xref)
                        img = Image.open(io.BytesIO(base_image["image"]))
                        
                        if img.width > 100 and img.height > 100:
                            all_images.append(img)
                            image_map.append((page_num, len(page_info["image_results"])))
                            page_info["image_results"].append(None)
                            
                    except Exception:
                        continue
            
            elif images:
                has_full_page = any(self._is_full_page_image(page, img_info) for img_info in images)
                
                if has_full_page:
                    mat = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    
                    all_images.append(img)
                    image_map.append((page_num, 0))
                    page_info["is_full_page_image"] = True
                    page_info["image_results"].append(None)
                else:
                    for img_info in images:
                        try:
                            xref = img_info[0]
                            base_image = pdf_document.extract_image(xref)
                            img = Image.open(io.BytesIO(base_image["image"]))
                            
                            if img.width > 100 and img.height > 100:
                                all_images.append(img)
                                image_map.append((page_num, len(page_info["image_results"])))
                                page_info["image_results"].append(None)

                        except Exception:
                            continue
            
            else:
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                
                all_images.append(img)
                image_map.append((page_num, 0))
                page_info["is_full_page_image"] = True
                page_info["image_results"].append(None)
            
            pages_data.append(page_info)
        
        if all_images:
            results = await loop.run_in_executor(None, self._process_images_parallel, all_images)
            
            for i, (page_idx, img_idx) in enumerate(image_map):
                pages_data[page_idx]["image_results"][img_idx] = results[i]
        
        documents = []
        
        for page_info in pages_data:
            page_num = page_info["page_num"]
            text = page_info["text"]
            image_results = [r for r in page_info["image_results"] if r]
            
            if page_info["has_text"]:
                content_parts = [text]
                for i, result in enumerate(image_results):
                    img_content = self._format_image_content(result, i + 1)
                    if img_content:
                        content_parts.append(img_content)
                
                documents.append(Document(
                    page_content="\n\n".join(content_parts),
                    metadata={"page": page_num + 1, "source": file_path, "method": "native"}
                ))
            
            elif page_info["is_full_page_image"] and image_results:
                result = image_results[0]
                content_parts = []
                
                if text:
                    content_parts.append(text)
                
                if result["description"]:
                    content_parts.append(f"[Imagem {page_num + 1}: {result['description']}]")
                
                if result["ocr"] and len(result["ocr"]) > 10:
                    content_parts.append(f"[Texto: {result['ocr']}]")
                
                if content_parts:
                    documents.append(Document(
                        page_content="\n\n".join(content_parts),
                        metadata={"page": page_num + 1, "source": file_path, "method": "vision+ocr"}
                    ))
            
            elif image_results:
                content_parts = []
                if text:
                    content_parts.append(text)
                
                for i, result in enumerate(image_results):
                    img_content = self._format_image_content(result, i + 1)
                    if img_content:
                        content_parts.append(img_content)
                
                if content_parts:
                    documents.append(Document(
                        page_content="\n\n".join(content_parts),
                        metadata={"page": page_num + 1, "source": file_path, "method": "mixed"}
                    ))

        pdf_document.close()

        return documents

    async def add_vectors(self, source_id: str, file_path: str) -> Tuple[bool, int]:       
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            pages = await self._extract_pdf_content(file_path)
            
            documents = self.text_splitter.split_documents(pages)
            chunks_count = len(documents)
            
            for i, doc in enumerate(documents):
                doc.metadata["source_id"] = source_id
                doc.metadata["chunk_index"] = i
            
            await loop.run_in_executor(
                None,
                lambda: MongoDBAtlasVectorSearch.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    collection=self.collection,
                    index_name=self.index_name
                )
            )
            
            return True, chunks_count
        
        except Exception:
            raise
    
    async def delete_vectors(self, source_id: str) -> bool:
        try:
            self.collection.delete_many({"source_id": source_id})
            
            return True
        
        except Exception:
            raise
    
    async def get_retriever(self, source_id: str) -> Any:
        try:
            vectordb = MongoDBAtlasVectorSearch(
                collection=self.collection,
                embedding=self.embeddings,
                index_name=self.index_name
            )
        
            retriever = vectordb.as_retriever(
                search_type='similarity',
                search_kwargs={
                    "k": 10,
                    "fetch_k": 50,
                    'pre_filter': {'source_id': str(source_id)}
                }
            )

            return NeighborRetriever(retriever, self.collection, source_id)
        
        except Exception:
            raise