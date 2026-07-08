> 🤖 이 프로젝트는 vibe coding 방식으로 만든 개인용 자동화 프로젝트입니다. 빠르게 실험하고 개선하는 것을 목표로 하며, 투자 판단용 공식 리서치 도구가 아닙니다.

# Stock Info

매일 미국 주식 리포트를 생성하는 도구입니다. HTML 리포트를 만들고, 같은 내용을 Edge/Chrome으로 PDF로 출력하며, Gmail SMTP를 통해 메일로 발송할 수 있습니다.

## 빠른 시작

```powershell
Copy-Item .env.example .env
$env:PYTHONPATH = "$PWD\src"
python -m stock_info.cli --sample-data --dry-run --force
```

생성된 파일은 `output/reports/us/YYYY-MM-DD/` 아래에 저장됩니다.

## 실시간 데이터

보유한 API 키를 `.env`에 입력하세요.

- `FMP_API_KEY`: 시세, 주식 뉴스, 실적 캘린더
- `FINNHUB_API_KEY`: 시장/기업 뉴스 보조 데이터
- `ALPHAVANTAGE_API_KEY`: 상승/하락 상위 종목
- `FRED_API_KEY`: 금리 등 매크로 지표

## API 키 발급 방법

먼저 `.env.example`을 복사해 `.env`를 만듭니다.

```powershell
Copy-Item .env.example .env
```

그다음 아래 서비스 중 사용할 것만 발급받아 `.env`에 넣으면 됩니다. 모든 키가 필수는 아니며, 키가 없으면 해당 데이터는 비어 있거나 샘플 데이터로 대체됩니다.

### Financial Modeling Prep

FMP는 시세, 주식 뉴스, 실적 캘린더 수집에 사용합니다.

1. [FMP 회원가입 페이지](https://site.financialmodelingprep.com/register)에 접속합니다.
2. 이메일/비밀번호 또는 Google 계정으로 가입합니다.
3. 이메일 인증 후 대시보드에서 API Key를 확인합니다.
4. `.env`에 아래처럼 입력합니다.

```env
FMP_API_KEY=발급받은_FMP_API_KEY
```

공식 문서: <https://site.financialmodelingprep.com/developer/docs>

### Finnhub

Finnhub는 시장 뉴스와 기업 뉴스 보조 데이터로 사용합니다.

1. [Finnhub 회원가입 페이지](https://finnhub.io/register)에 접속합니다.
2. 계정을 만든 뒤 로그인합니다.
3. 대시보드에서 API Key를 복사합니다.
4. `.env`에 아래처럼 입력합니다.

```env
FINNHUB_API_KEY=발급받은_FINNHUB_API_KEY
```

공식 문서: <https://finnhub.io/docs/api>

### Alpha Vantage

Alpha Vantage는 상승/하락 상위 종목 데이터에 사용합니다.

1. [Alpha Vantage API 키 발급 페이지](https://www.alphavantage.co/support/#api-key)에 접속합니다.
2. 사용자 유형, 조직명, 이메일을 입력합니다.
3. 무료 API Key를 발급받습니다.
4. `.env`에 아래처럼 입력합니다.

```env
ALPHAVANTAGE_API_KEY=발급받은_ALPHA_VANTAGE_API_KEY
```

무료 사용량 제한이 있으므로, 호출량이 늘어나면 유료 플랜이 필요할 수 있습니다.

공식 문서: <https://www.alphavantage.co/documentation/>

### FRED

FRED는 미국 금리 등 매크로 지표 수집에 사용합니다.

1. [FRED API Key 페이지](https://fred.stlouisfed.org/docs/api/api_key.html)에 접속합니다.
2. FRED 계정으로 로그인하거나 계정을 새로 만듭니다.
3. `Request or view your API keys`에서 API Key를 생성합니다.
4. `.env`에 아래처럼 입력합니다.

```env
FRED_API_KEY=발급받은_FRED_API_KEY
```

공식 문서: <https://fred.stlouisfed.org/docs/api/fred/>

### Gmail 앱 비밀번호

Gmail SMTP로 메일을 보내려면 일반 비밀번호가 아니라 앱 비밀번호를 사용해야 합니다.

1. Google 계정에서 2단계 인증을 켭니다.
2. [Google 앱 비밀번호 페이지](https://myaccount.google.com/apppasswords)에 접속합니다.
3. 앱 비밀번호를 생성하고 16자리 비밀번호를 복사합니다.
4. `.env`에 아래처럼 입력합니다.

```env
SMTP_USER=your_account@gmail.com
SMTP_APP_PASSWORD=발급받은_앱_비밀번호
MAIL_TO=recipient@example.com
```

앱 비밀번호 메뉴가 보이지 않는 경우 조직 계정, 보안 키 전용 2단계 인증, 고급 보호 설정 때문에 제한될 수 있습니다.

공식 도움말: <https://support.google.com/mail/answer/185833>

실행:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m stock_info.cli --live --dry-run
```

API 키가 없으면 샘플 데이터 리포트로 자동 대체되며, 리포트 안에 샘플 데이터임이 표시됩니다.

## 이메일 발송

Gmail을 사용하려면 앱 비밀번호를 만든 뒤 아래 값을 설정하세요.

```env
SMTP_USER=your_account@gmail.com
SMTP_APP_PASSWORD=your_app_password
MAIL_TO=recipient@example.com
```

발송:

```powershell
.\scripts\run_us_report.cmd -Send
```

`.ps1` 파일을 직접 실행했을 때 메모장이 열리면 PowerShell 스크립트가 실행된 것이 아니라 Windows 파일 연결로 열린 것입니다. 이 경우 위처럼 `.cmd` 파일을 실행하거나, 아래 명령처럼 PowerShell을 명시해서 실행하세요.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\run_us_report.ps1" -Send
```

## Windows 작업 스케줄러

평일 한국시간 21:00에 실행되는 작업을 등록합니다.

```powershell
.\scripts\create_windows_task.cmd -Time "21:00"
```

등록된 작업은 `scripts/run_us_report.ps1 -Send`를 PowerShell로 실행합니다.

## 참고 사항

`config/us_report.toml`에 있는 주식 전문 사이트들은 기본적으로 참고 링크로만 사용됩니다. 금융 사이트는 자동 재사용을 제한하는 경우가 많고, 페이지 구조나 접근 정책이 예고 없이 바뀔 수 있으므로 이 MVP에서는 직접 페이지 스크래핑을 피합니다.
