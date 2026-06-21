import requests

# ===== 1. 스포티파이 API 키 (본인 값 그대로 사용) =====
CLIENT_ID = "e6d8ff575f0745c6b7aaabc81330377f"
CLIENT_SECRET = "d71cc84f186c4e3d8d0814b5bf5f7293"

# ===== 2. API 엔드포인트 =====
TOKEN_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"

# ===== 3. 트렌드 추적할 장르 키워드 (필요하면 자유롭게 수정) =====
GENRES = ["pop", "k-pop", "hip-hop", "latin", "rock", "electronic", "r&b"]

TOP_N = 10  # 최종 TrendScan Top N


def get_access_token():
    """Client Credentials 방식으로 Access Token 발급"""
    try:
        response = requests.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(CLIENT_ID, CLIENT_SECRET),
            timeout=10,
        )

        if response.status_code != 200:
            print("❌ 토큰 발급 실패!")
            print(f"상태 코드: {response.status_code}")
            print(f"응답 내용: {response.text}")
            return None

        return response.json().get("access_token")

    except requests.exceptions.RequestException as e:
        print(f"❌ 토큰 요청 중 네트워크 오류 발생: {e}")
        return None


def search_tracks_by_genre(access_token, genre, limit=10):
    """장르 키워드로 트랙 검색"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "q": f"genre:{genre}",
        "type": "track",
        "limit": limit,
    }

    try:
        response = requests.get(
            SEARCH_URL,
            headers=headers,
            params=params,
            timeout=10,
        )

        if response.status_code != 200:
            print(f"❌ '{genre}' 장르 검색 실패! 상태 코드: {response.status_code}")
            print(f"응답 내용: {response.text}")
            return []

        return response.json().get("tracks", {}).get("items", [])

    except requests.exceptions.RequestException as e:
        print(f"❌ '{genre}' 검색 중 네트워크 오류 발생: {e}")
        return []


def build_trendscan_top(access_token):
    """여러 장르 검색 결과를 합쳐 popularity 기준 Top N 산출"""
    collected = {}  # track_id -> track 정보 (중복 제거용)

    for genre in GENRES:
        items = search_tracks_by_genre(access_token, genre, limit=10)
        print(f"  - '{genre}' 장르에서 {len(items)}곡 수집")

        for track in items:
            track_id = track.get("id")
            if track_id and track_id not in collected:
                collected[track_id] = track

    sorted_tracks = sorted(
        collected.values(),
        key=lambda t: t.get("popularity", 0),
        reverse=True,
    )

    return sorted_tracks[:TOP_N]


def print_top_tracks(tracks):
    """차트 데이터를 보기 좋게 출력"""
    if not tracks:
        print("출력할 데이터가 없습니다.")
        return

    print("=" * 60)
    print(f"🔥 TrendScan Top {TOP_N} (자체 산출 인기 차트)")
    print("=" * 60)

    for idx, track in enumerate(tracks, start=1):
        title = track.get("name", "제목 없음")
        artists = ", ".join(
            artist.get("name", "") for artist in track.get("artists", [])
        )
        album = track.get("album", {}).get("name", "앨범 정보 없음")
        popularity = track.get("popularity", "N/A")

        print(f"{idx}. {title} - {artists} (앨범: {album}, 인기도: {popularity})")

    print("=" * 60)


def main():
    # 1) 토큰 발급
    access_token = get_access_token()
    if not access_token:
        print("토큰을 발급받지 못해 프로그램을 종료합니다.")
        return

    # 2) 장르별 검색 + 인기도 기준 Top N 산출
    print("📡 장르별 트랙 수집 중...")
    top_tracks = build_trendscan_top(access_token)

    if not top_tracks:
        print("차트 데이터를 가져오지 못해 프로그램을 종료합니다.")
        return

    # 3) 결과 출력
    print_top_tracks(top_tracks)


if __name__ == "__main__":
    main()