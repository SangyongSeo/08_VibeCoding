#!/usr/bin/env python3
"""
간단한 환율 조회 프로그램
ExchangeRate API를 사용하여 실시간 환율 정보를 조회합니다.
(API 키 불필요)
"""

import requests
import sys
from datetime import datetime


# 주요 통화 코드와 이름
CURRENCY_NAMES = {
    "KRW": "한국 원",
    "USD": "미국 달러",
    "EUR": "유로",
    "JPY": "일본 엔",
    "GBP": "영국 파운드",
    "CNY": "중국 위안",
    "CHF": "스위스 프랑",
    "CAD": "캐나다 달러",
    "AUD": "호주 달러",
    "NZD": "뉴질랜드 달러",
    "HKD": "홍콩 달러",
    "SGD": "싱가포르 달러",
    "SEK": "스웨덴 크로나",
    "NOK": "노르웨이 크로네",
    "MXN": "멕시코 페소",
    "INR": "인도 루피",
    "BRL": "브라질 헤알",
    "THB": "태국 바트",
}

# API 기본 URL
API_BASE_URL = "https://open.er-api.com/v6/latest"


def get_exchange_rate(base: str) -> dict:
    """환율 정보를 가져옵니다."""
    url = f"{API_BASE_URL}/{base.upper()}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("result") != "success":
        raise Exception("API 요청 실패")

    return data


def display_rates(data: dict, target: str = None, show_all: bool = False) -> None:
    """환율 정보를 보기 좋게 출력합니다."""
    base = data["base_code"]
    rates = data["rates"]
    update_time = data.get("time_last_update_utc", "N/A")

    base_name = CURRENCY_NAMES.get(base, base)

    print("\n" + "=" * 50)
    print(f"💱 환율 정보 (기준: 1 {base} = {base_name})")
    print(f"📅 업데이트: {update_time[:16]}")
    print("=" * 50)

    # 특정 통화만 표시
    if target:
        if target in rates:
            rate = rates[target]
            name = CURRENCY_NAMES.get(target, target)
            print(f"  {target}: {rate:,.4f} ({name})")
        else:
            print(f"  ❌ {target} 통화를 찾을 수 없습니다.")
    # 주요 통화만 표시하거나 전체 표시
    elif show_all:
        for currency in sorted(rates.keys()):
            rate = rates[currency]
            name = CURRENCY_NAMES.get(currency, "")
            if name:
                print(f"  {currency}: {rate:,.4f} ({name})")
            else:
                print(f"  {currency}: {rate:,.4f}")
    else:
        display_currencies = ["KRW", "USD", "EUR", "JPY", "GBP", "CNY"]
        for currency in display_currencies:
            if currency in rates and currency != base:
                rate = rates[currency]
                name = CURRENCY_NAMES.get(currency, currency)
                print(f"  {currency}: {rate:,.4f} ({name})")

        remaining = len(rates) - len(display_currencies)
        if remaining > 0:
            print(f"\n  ... 외 {remaining}개 통화")
            print("  (전체 보기: 'USD all' 형식으로 입력)")

    print("=" * 50 + "\n")


def display_conversion(rates: dict, amount: float, base: str, target: str) -> None:
    """환전 결과를 출력합니다."""
    if target not in rates:
        print(f"❌ {target} 통화를 찾을 수 없습니다.\n")
        return

    rate = rates[target]
    result = amount * rate
    base_name = CURRENCY_NAMES.get(base, base)
    target_name = CURRENCY_NAMES.get(target, target)

    print("\n" + "=" * 50)
    print("💰 환전 결과")
    print("=" * 50)
    print(f"  {amount:,.2f} {base} ({base_name})")
    print(f"  ↓")
    print(f"  {result:,.2f} {target} ({target_name})")
    print(f"\n  환율: 1 {base} = {rate:,.4f} {target}")
    print("=" * 50 + "\n")


def show_help():
    """도움말을 표시합니다."""
    print("""
╔══════════════════════════════════════════════════╗
║         💱 환율 조회 프로그램 도움말                ║
╠══════════════════════════════════════════════════╣
║  명령어 사용법:                                   ║
║                                                  ║
║  • USD          → USD 기준 주요 환율 조회         ║
║  • USD all      → USD 기준 전체 환율 조회         ║
║  • USD KRW      → USD → KRW 환율만 조회          ║
║  • 100 USD KRW  → 100 USD를 KRW로 환전           ║
║                                                  ║
║  • help         → 이 도움말 보기                  ║
║  • quit / q     → 프로그램 종료                   ║
╚══════════════════════════════════════════════════╝
""")


def parse_input(user_input: str) -> tuple:
    """사용자 입력을 파싱합니다."""
    parts = user_input.upper().split()

    if len(parts) == 1:
        # "USD" → USD 기준 환율
        return (None, parts[0], None, False)
    elif len(parts) == 2:
        # "USD all" 또는 "USD KRW"
        if parts[1] == "ALL":
            return (None, parts[0], None, True)
        else:
            return (None, parts[0], parts[1], False)
    elif len(parts) == 3:
        # "100 USD KRW" → 환전
        try:
            amount = float(parts[0].replace(",", ""))
            return (amount, parts[1], parts[2], False)
        except ValueError:
            return (None, None, None, False)

    return (None, None, None, False)


def main():
    """메인 함수"""
    print("\n💱 환율 조회 프로그램")
    print("API 키 없이 실시간 환율을 조회합니다.")
    print("'help'를 입력하면 사용법을 볼 수 있습니다.\n")

    while True:
        try:
            user_input = input("조회할 통화를 입력하세요 (예: USD, 100 USD KRW): ").strip()

            if not user_input:
                continue

            lower_input = user_input.lower()

            if lower_input in ["quit", "q", "exit"]:
                print("프로그램을 종료합니다. 👋\n")
                break
            elif lower_input == "help":
                show_help()
                continue

            amount, base, target, show_all = parse_input(user_input)

            if not base:
                print("❌ 올바른 형식으로 입력해주세요. 'help'로 사용법을 확인하세요.\n")
                continue

            # API 호출
            data = get_exchange_rate(base)
            rates = data["rates"]

            if amount and target:
                # 환전 모드
                display_conversion(rates, amount, base, target)
            elif target:
                # 특정 통화 환율 조회
                display_rates(data, target=target)
            else:
                # 기준 통화 환율 조회
                display_rates(data, show_all=show_all)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print("❌ 지원하지 않는 통화 코드입니다.\n")
            else:
                print(f"❌ API 오류: {e}\n")
        except requests.exceptions.ConnectionError:
            print("❌ 인터넷 연결을 확인해주세요.\n")
        except requests.exceptions.Timeout:
            print("❌ 요청 시간이 초과되었습니다. 다시 시도해주세요.\n")
        except Exception as e:
            print(f"❌ 오류 발생: {e}\n")


if __name__ == "__main__":
    main()
