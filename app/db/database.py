import json
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
from rapidfuzz import fuzz, process

class SearchmarkDatabase:
    def __init__(self, json_path: str):
        """
        상표 검색 데이터베이스 초기화
        
        Args:
            json_path: 상표 데이터가 저장된 JSON 파일 경로
        """
        self.json_path = json_path
        self.data = self._load_data(json_path)
        
    def _load_data(self, json_path: str) -> List[Dict[str, Any]]:
        """
        JSON 파일에서 데이터 로드
        
        Args:
            json_path: JSON 파일 경로
            
        Returns:
            로드된 데이터 리스트
            
        Raises:
            FileNotFoundError: 파일을 찾을 수 없는 경우
            json.JSONDecodeError: JSON 형식이 올바르지 않은 경우
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {json_path}")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"올바르지 않은 JSON 형식입니다: {json_path}", "", 0)
    
    
    def search_searchmarks(
        self,
        productName: Optional[str] = None, # 상표명 또는 영문명에서 검색할 키워드
        status: Optional[str] = None, # 필터링할 등록 상태
        applicationNumber: Optional[str] = None, # 출원번호로 검색
        publicationNumber: Optional[str] = None, # 공고번호로 검색
        registrationNumber: Optional[str] = None, # 등록번호로 검색
        internationalRegNumbers: Optional[str] = None, # 국제등록번호로 검색
        priorityClaimNumList: Optional[str] = None, # 우선권주장번호로 검색
        asignProductMainCodeList: Optional[str] = None, # 상품 주 분류코드로 검색 (쉼표로 구분된 여러 코드 가능, 한 자리 수는 앞에 0이 자동으로 붙음)
        viennaCodeList: Optional[str] = None, # 비엔나 코드 리스트로 검색 (쉼표로 구분된 여러 코드 가능, 한 자리 수는 앞에 0이 자동으로 붙음)
        limit: int = 10,
        use_fuzzy_search: bool = False  # 유사도 검색 사용 여부
    ) -> List[Dict[str, Any]]:
        """
        상표 데이터 검색
        
        Args:
            productName: 상표명 또는 영문명에서 검색할 키워드
            status: 필터링할 등록 상태
            applicationNumber: 출원번호로 검색
            publicationNumber: 공고번호로 검색
            registrationNumber: 등록번호로 검색
            internationalRegNumbers: 국제등록번호로 검색
            priorityClaimNumList: 우선권주장번호로 검색
            asignProductMainCodeList: 상품 주 분류코드로 검색 (쉼표로 구분된 여러 코드 가능, 한 자리 수는 앞에 0이 자동으로 붙음)
            viennaCodeList: 비엔나 코드 리스트로 검색 (쉼표로 구분된 여러 코드 가능, 한 자리 수는 앞에 0이 자동으로 붙음)
            limit: 반환할 최대 결과 수
            use_fuzzy_search: 유사도 검색 사용 여부

        Returns:
            검색 조건에 맞는 결과 리스트
        """
        results = self.data.copy()
        
        # 키워드 검색 (상표명 또는 영문명)
        # 검색 키워드는 대소문자 구분 없이 검색
        if productName:
            productName = productName.lower()
            if use_fuzzy_search:
                # 유사도 검색 결과
                fuzzy_results = []
                for item in results:
                    korean_score = 0
                    eng_score = 0
                    
                    if item.get('productName'):
                        korean_score = fuzz.ratio(productName, item['productName'].lower())
                    
                    if item.get('productNameEng'):
                        eng_score = fuzz.ratio(productName, item['productNameEng'].lower())
                    
                    similarity_score = max(korean_score, eng_score)
                    
                    if similarity_score >= 40:  # 유사도 40% 이상
                        item['similarity_score'] = similarity_score
                        fuzzy_results.append(item)
                
                # 유사도 점수로 정렬
                results = sorted(fuzzy_results, key=lambda x: x['similarity_score'], reverse=True)
            else:
                # 기존 검색 방식
                results = [
                    item for item in results
                    if (item.get('productName') and productName in item['productName']) or
                        (item.get('productNameEng') and productName in item['productNameEng'])
                ]
        
        # 등록 상태 필터링
        if status:
            results = [item for item in results if item.get('registerStatus') == status]
        
        # 상품 주 분류코드 필터링
        if asignProductMainCodeList:
            # 쉼표로 구분된 코드들을 리스트로 변환
            code_list = [code.strip() for code in asignProductMainCodeList.split(',')]
            
            # 각 코드에 대해 한 자리 수인 경우 앞에 0을 붙임
            formatted_codes = []
            for code in code_list:
                try:
                    num_code = int(code)
                    if num_code < 10:
                        formatted_codes.append(f"0{code}")  # 한 자리 수인 경우 앞에 0을 붙임
                    else:
                        formatted_codes.append(code)
                except ValueError:
                    formatted_codes.append(code)  # 숫자가 아닌 경우 그대로 사용
            
            results = [
                item for item in results
                if item.get('asignProductMainCodeList') and 
                any(code in item['asignProductMainCodeList'] for code in formatted_codes)
            ]
        
        # 상품 코드 필터링
        if applicationNumber:
            results = [
                item for item in results
                if item.get('applicationNumber') and 
                applicationNumber in item['applicationNumber']
            ]
        
        if publicationNumber:
            results = [
                item for item in results
                if item.get('publicationNumber') and 
                publicationNumber in item['publicationNumber']
            ]
        
        if registrationNumber:
            results = [
                item for item in results
                if item.get('registrationNumber') and 
                registrationNumber in item['registrationNumber']
            ]
        
        if internationalRegNumbers:
            results = [
                item for item in results
                if item.get('internationalRegNumbers') and 
                internationalRegNumbers in item['internationalRegNumbers']
            ]

        if priorityClaimNumList:
            results = [
                item for item in results
                if item.get('priorityClaimNumList') and 
                priorityClaimNumList in item['priorityClaimNumList']
            ]

        if viennaCodeList:
            results = [
                item for item in results
                if item.get('viennaCodeList') and 
                viennaCodeList in item['viennaCodeList']
            ]
            
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        데이터베이스 통계 정보 반환
        
        Returns:
            통계 정보를 담은 딕셔너리
        """
        if not self.data:
            return {"total": 0}
        
        status_counts = {}
        for item in self.data:
            status = item.get('registerStatus', '미분류')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total": len(self.data),
            "status_counts": status_counts
        }
    
    def to_pandas(self) -> pd.DataFrame:
        """
        데이터를 Pandas DataFrame으로 변환
        
        Returns:
            상표 데이터가 포함된 DataFrame
        """
        return pd.DataFrame(self.data)
    
