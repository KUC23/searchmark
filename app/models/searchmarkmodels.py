from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class SearchmarkBase(BaseModel):
    productName: Optional[str] = None # 상표명
    productNameEng: Optional[str] = None # 영문명
    applicationNumber: Optional[str] = None # 출원번호
    applicationDate: Optional[str] = None # 출원일
    registerStatus: Optional[str] = None # 등록상태
    publicationNumber: Optional[str] = None # 공고번호
    publicationDate: Optional[str] = None # 공고일
    registrationNumber: Optional[List[str]] = None # 등록번호
    registrationDate: Optional[List[str]] = None # 등록일
    asignProductMainCodeList: Optional[List[str]] = None # 상품 주 분류 코드
    asignProductSubCodeList: Optional[List[str]] = None # 상품 부 분류 코드
    viennaCodeList: Optional[List[str]] = None # 빈티나 분류 코드

class SearchmarkResponse(SearchmarkBase):
    class Config:
        from_attributes = True # 모델 필드를 데이터베이스 필드에 매핑

class PaginatedResponse(BaseModel):
    total: int
    total_pages: int
    limit: int
    data: List[SearchmarkResponse]