from __future__ import annotations

from datetime import date, datetime

from ..models import EventItem, MacroPoint, NewsItem, Quote, ReportData


def build_sample_report(
    report_date: date,
    generated_at: datetime,
    title_prefix: str,
    references: dict[str, str],
) -> ReportData:
    title = f"{report_date.month}월 {report_date.day}일 {title_prefix}"
    return ReportData(
        report_date=report_date,
        generated_at=generated_at,
        title=title,
        subtitle="API 키 없이 생성한 샘플 리포트",
        headline="AI 반도체, 금리, 실적 일정이 미국주식 시장의 중심 변수",
        summary=(
            "오늘 리포트는 자동화 파이프라인 검증용 샘플 데이터입니다. "
            "실제 운용에서는 .env에 API 키를 넣으면 같은 양식으로 라이브 데이터가 채워집니다."
        ),
        is_sample=True,
        market_snapshot=[
            Quote("SPY", "S&P 500 ETF", 637.42, 1.12, 0.18, 42_100_000, "sample"),
            Quote("QQQ", "Nasdaq 100 ETF", 565.31, 2.44, 0.43, 51_800_000, "sample"),
            Quote("DIA", "Dow 30 ETF", 444.27, -0.38, -0.09, 8_700_000, "sample"),
            Quote("IWM", "Russell 2000 ETF", 219.18, 0.96, 0.44, 29_300_000, "sample"),
            Quote("VIXY", "VIX Futures ETF", 11.82, -0.21, -1.75, 3_400_000, "sample"),
        ],
        movers_up=[
            Quote("NVDA", "NVIDIA", 167.21, 5.10, 3.15, 92_500_000, "sample", "AI 수요 기대"),
            Quote("AVGO", "Broadcom", 287.40, 6.72, 2.39, 18_900_000, "sample", "반도체 강세"),
            Quote("PLTR", "Palantir", 141.06, 3.22, 2.34, 38_100_000, "sample", "기관 수급"),
        ],
        movers_down=[
            Quote("TSLA", "Tesla", 297.88, -7.14, -2.34, 75_600_000, "sample", "인도량 경계"),
            Quote("META", "Meta Platforms", 704.11, -8.05, -1.13, 14_200_000, "sample", "CapEx 부담"),
            Quote("AMD", "Advanced Micro Devices", 152.62, -1.94, -1.26, 31_700_000, "sample", "차익실현"),
        ],
        watchlist=[
            Quote("AAPL", "Apple", 214.31, 0.84, 0.39, 46_300_000, "sample"),
            Quote("MSFT", "Microsoft", 507.89, 1.92, 0.38, 20_600_000, "sample"),
            Quote("AMZN", "Amazon", 223.48, -0.72, -0.32, 30_100_000, "sample"),
            Quote("GOOGL", "Alphabet", 178.26, 0.16, 0.09, 24_700_000, "sample"),
        ],
        macro_points=[
            MacroPoint("미 10년물 금리", "4.28%", "sample", "전일 대비 소폭 상승"),
            MacroPoint("달러 인덱스", "105.1", "sample", "위험자산과 동반 관찰"),
            MacroPoint("WTI", "$82.40", "sample", "에너지 섹터 민감"),
        ],
        news=[
            NewsItem(
                "대형 기술주 수급이 지수 방향성을 주도",
                "sample",
                "https://finance.yahoo.com/",
                "AI 인프라 투자와 반도체 업종 실적 기대가 시장의 중심 테마로 남아 있습니다.",
            ),
            NewsItem(
                "이번 주 실적 발표 기업에 관심 집중",
                "sample",
                "https://www.investing.com/earnings-calendar/",
                "장 전후 실적 이벤트가 개별 종목 변동성을 키울 수 있습니다.",
            ),
            NewsItem(
                "금리와 달러 흐름은 성장주 밸류에이션의 단기 변수",
                "sample",
                "https://fred.stlouisfed.org/",
                "국채금리 변화가 기술주 멀티플에 영향을 줄 수 있어 함께 점검합니다.",
            ),
        ],
        events=[
            EventItem("Before Open", "주요 기업 실적 발표 체크", "sample", ["STZ", "WBA"]),
            EventItem("09:30 ET", "미국 정규장 개장", "sample", []),
            EventItem("After Close", "장 마감 후 실적/가이던스 확인", "sample", ["LEVI"]),
        ],
        references=references,
        warnings=["샘플 데이터입니다. 투자 판단에 사용하지 마세요."],
    )
