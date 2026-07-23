import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ---------------------------------------------------------
# 1) 페이지 기본 설정
#    - 브라우저 탭 제목과 아이콘, 화면 레이아웃을 정해줘요.
# ---------------------------------------------------------
st.set_page_config(page_title="약속 잡기", page_icon="🗓️", layout="centered")

# ---------------------------------------------------------
# 2) Supabase 연결하기
#    - secrets(비밀 금고)에 저장해둔 URL과 KEY를 불러와서 연결해요.
#    - streamlit cloud에 배포할 때는 앱 설정의 Secrets 메뉴에
#      SUPABASE_URL = "..." 
#      SUPABASE_KEY = "..."
#      이렇게 두 줄을 넣어주면 됩니다.
# ---------------------------------------------------------
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase_client()

# ---------------------------------------------------------
# 3) 화면에 보여줄 제목과 설명
# ---------------------------------------------------------
st.title("🗓️ 약속 잡기")
st.write("모두가 편한 시간을 찾기 위해, 이름과 가능한 시간을 알려주세요 :)")

st.divider()

# ---------------------------------------------------------
# 4) 선택 가능한 시간 목록
#    - 필요에 맞게 아래 리스트의 문구를 자유롭게 수정해서 쓰세요.
# ---------------------------------------------------------
TIME_OPTIONS = [
    "월요일 오전",
    "월요일 오후",
    "화요일 오전",
    "화요일 오후",
    "수요일 오전",
    "수요일 오후",
    "목요일 오전",
    "목요일 오후",
    "금요일 오전",
    "금요일 오후",
]

# ---------------------------------------------------------
# 5) 입력 폼 (이름 + 가능한 시간 + 제출 버튼)
#    - st.form을 쓰면 '제출' 버튼을 누를 때 한 번에 값이 전달돼요.
# ---------------------------------------------------------
with st.form("vote_form", clear_on_submit=True):
    name = st.text_input("이름을 입력해주세요")
    times = st.multiselect("가능한 시간을 모두 골라주세요", options=TIME_OPTIONS)

    submitted = st.form_submit_button("제출")

    if submitted:
        # 이름이 비어있거나 시간을 하나도 안 골랐으면 안내만 하고 저장하지 않아요.
        if not name.strip():
            st.warning("이름을 입력해주세요!")
        elif not times:
            st.warning("가능한 시간을 최소 한 개 이상 골라주세요!")
        else:
            # 여러 시간을 콤마로 이어붙여서 하나의 문자열(text)로 저장해요.
            times_text = ", ".join(times)

            # ------------------------------------------
            # votes 테이블에 한 줄 추가하기 (insert)
            # ------------------------------------------
            try:
                supabase.table("votes").insert(
                    {"name": name.strip(), "times": times_text}
                ).execute()
                st.success(f"{name}님, 제출이 완료되었어요! 감사합니다 🙌")
            except Exception as e:
                st.error(f"저장 중 문제가 발생했어요: {e}")

st.divider()

# ---------------------------------------------------------
# 6) 지금까지 제출된 전체 명단 보여주기
#    - votes 테이블의 모든 데이터를 읽어와서 표로 그려줘요.
# ---------------------------------------------------------
st.subheader("📋 지금까지 제출된 명단")

try:
    response = supabase.table("votes").select("*").execute()
    rows = response.data  # 리스트(list) 형태의 데이터가 들어있어요.

    if rows:
        df = pd.DataFrame(rows)

        # 화면에 보여줄 때는 이름, 가능시간 위주로 보기 좋게 정리해요.
        display_columns = [col for col in ["name", "times"] if col in df.columns]
        st.dataframe(df[display_columns], use_container_width=True, hide_index=True)
    else:
        st.info("아직 제출된 내용이 없어요. 첫 번째로 제출해보세요!")
except Exception as e:
    st.error(f"명단을 불러오는 중 문제가 발생했어요: {e}")
