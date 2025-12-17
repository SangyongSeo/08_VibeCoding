#!/usr/bin/env python3
"""
간단한 날씨 조회 프로그램
OpenWeatherMap API를 사용하여 도시별 날씨 정보를 조회합니다.
"""

import requests
import sys
import os
from datetime import datetime


def get_weather(city: str, api_key: str) -> dict:
    """OpenWeatherMap API를 통해 날씨 정보를 가져옵니다."""
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",  # 섭씨 온도 사용
        "lang": "kr"  # 한국어 설명
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()


def display_weather(data: dict) -> None:
    """날씨 정보를 보기 좋게 출력합니다."""
    city = data["name"]
    country = data["sys"]["country"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    description = data["weather"][0]["description"]
    wind_speed = data["wind"]["speed"]

    # 일출/일몰 시간 변환
    sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
    sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")

    print("\n" + "=" * 40)
    print(f"🌍 {city}, {country} 날씨 정보")
    print("=" * 40)
    print(f"🌡️  현재 온도: {temp}°C")
    print(f"🤔 체감 온도: {feels_like}°C")
    print(f"💧 습도: {humidity}%")
    print(f"☁️  날씨: {description}")
    print(f"💨 풍속: {wind_speed} m/s")
    print(f"🌅 일출: {sunrise}")
    print(f"🌇 일몰: {sunset}")
    print("=" * 40 + "\n")


def main():
    """메인 함수"""
    # API 키 확인 (환경변수 또는 직접 입력)
    api_key = os.environ.get("OPENWEATHER_API_KEY")

    if not api_key:
        print("OpenWeatherMap API 키가 필요합니다.")
        print("https://openweathermap.org/api 에서 무료 API 키를 발급받으세요.")
        print()
        api_key = input("API 키를 입력하세요: ").strip()

        if not api_key:
            print("API 키가 입력되지 않았습니다.")
            sys.exit(1)

    print("\n🌤️  날씨 조회 프로그램")
    print("종료하려면 'quit' 또는 'q'를 입력하세요.\n")

    while True:
        city = input("도시 이름을 입력하세요 (예: Seoul, Tokyo, London): ").strip()

        if city.lower() in ["quit", "q", "exit"]:
            print("프로그램을 종료합니다. 👋")
            break

        if not city:
            print("도시 이름을 입력해주세요.\n")
            continue

        try:
            weather_data = get_weather(city, api_key)
            display_weather(weather_data)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"❌ '{city}' 도시를 찾을 수 없습니다. 영문 이름으로 다시 시도해주세요.\n")
            elif e.response.status_code == 401:
                print("❌ API 키가 유효하지 않습니다.\n")
            else:
                print(f"❌ 오류가 발생했습니다: {e}\n")
        except requests.exceptions.ConnectionError:
            print("❌ 인터넷 연결을 확인해주세요.\n")
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}\n")


if __name__ == "__main__":
    main()
