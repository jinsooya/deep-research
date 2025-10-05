from datetime import datetime

def get_today_str() -> str:
    """
    오늘 날짜를 사람이 읽기 좋은 문자열 형식으로 반환한다.  

    Returns:
        str: '요일 월 일, 연도' 형식의 문자열  
             예: 'Mon Jan 1, 2025'
    """
    # 현재 시간을 가져와 지정된 문자열 포맷으로 변환한다.
    return datetime.now().strftime('%a %b %-d, %Y')