from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any, Optional
from app.models.searchmarkmodels import SearchmarkResponse
from app.db.database import SearchmarkDatabase
import os
import math

router = APIRouter(
    prefix="/searchmarks",
    tags=["searchmarks"]
)

# 데이터베이스 인스턴스 생성
db = SearchmarkDatabase(os.path.join("app/data", "trademark_sample.json"))

@router.get("/search", response_model=Dict[str, Any])

async def search_searchmarks(
    productName: str = Query(None, alias="productName(상표명)"),
    status: str = Query(None, alias="status(등록상태)"),
    applicationNumber: str = Query(None, alias="applicationNumber(출원번호)"),
    publicationNumber: str = Query(None, alias="publicationNumber(공고번호)"),
    registrationNumber: str = Query(None, alias="registrationNumber(등록번호)"),
    internationalRegNumbers: str = Query(None, alias="internationalRegNumbers(국제등록번호)"),
    priorityClaimNumList: str = Query(None, alias="priorityClaimNumList(우선권주장번호)"),
    asignProductMainCodeList: str = Query(None, alias="asignProductMainCodeList(상품주분류코드)"),
    viennaCodeList: str = Query(None, alias="viennaCodeList(비엔나분류코드)"),
    limit: int = 10,
    use_fuzzy_search: bool = Query(False, alias="use_fuzzy_search(유사도검색)")
):
    """
    상표 검색 API
    
    - **productName**: 상표명 또는 영문명으로 검색
    - **status**: 등록 상태로 필터링 (예: 등록, 실효, 거절)
    - **applicationNumber**: 출원번호로 검색
    - **publicationNumber**: 공고번호로 검색
    - **registrationNumber**: 등록번호로 검색
    - **internationalRegNumbers**: 국제등록번호로 검색
    - **priorityClaimNumList**: 우선권주장번호로 검색
    - **asignProductMainCodeList**: 상품 주 분류코드로 검색
    - **viennaCodeList**: 비엔나 코드 리스트로 검색
    - **limit**: 결과 수 제한 (기본값: 10)
    - **use_fuzzy_search**: 유사도 검색 사용 여부 (기본값: False)
    """
    # 검색 조건이 없는 경우 (limit 제외)
    search_params = [productName, status, applicationNumber, publicationNumber, registrationNumber, internationalRegNumbers, priorityClaimNumList, asignProductMainCodeList, viennaCodeList]
    if all(param is None for param in search_params):
        total_data = len(db.data)
        total_pages = math.ceil(total_data / limit)
        return {
            "total": total_data,
            "total_pages": total_pages,
            "limit": limit,
            "data": db.data[:limit]
        }
    
    # 검색 조건이 있는 경우 필터링 적용
    results = db.search_searchmarks(
        productName=productName,
        status=status,
        applicationNumber=applicationNumber,
        publicationNumber=publicationNumber,
        registrationNumber=registrationNumber,
        internationalRegNumbers=internationalRegNumbers,
        priorityClaimNumList=priorityClaimNumList,
        asignProductMainCodeList=asignProductMainCodeList,
        viennaCodeList=viennaCodeList,
        limit=None,
        use_fuzzy_search=use_fuzzy_search
    )
    
    
    # 페이지네이션을 위한 전체 검색 결과 수 계산
    total_results = len(results)
    
    # 페이지네이션을 위한 총 페이지 수 계산
    total_pages = math.ceil(total_results / limit)
    
    # limit 적용
    results = results[:limit]
    
    return {
        "total": total_results,
        "total_pages": total_pages,
        "limit": limit,
        "data": results
    } 