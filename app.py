import streamlit as st
import pandas as pd
import time
import re
from PIL import Image

# ==========================================
# 1. 페이지 기본 설정 및 디자인 (CSS)
# ==========================================
st.set_page_config(page_title="게임 성향 테스트", page_icon="🎮", layout="centered")

st.markdown("""
<style>
button[kind="primary"] {
    background-color: lightskyblue !important;
    color: black !important;
    border: 1px solid deepskyblue !important;
    font-weight: bold !important;
}
.result-box {
    background-color: #f0f8ff;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid lightskyblue;
    margin-bottom: 20px;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# 사용자 정보 노출 (과제 가이드 준수)
st.markdown("### 🎓 학번: 2023204005 | 이름: 양승모 (정보융합학부)")
st.markdown("---")

# ==========================================
# 2. 데이터 로드 및 캐싱
# ==========================================
@st.cache_data
def load_game_data():
    try:
        # 데이터가 정제되었으므로 이제 표준 방식으로 로드합니다.
        df = pd.read_csv('filtered_games.csv')
        df['Tags'] = df['Tags'].fillna('')
        df['Categories'] = df['Categories'].fillna('')
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

with st.spinner('게이머 데이터베이스 동기화 중...'):
    games_df = load_game_data()

# ==========================================
# 3. 16가지 성향 페르소나 데이터 (MBTI 매칭)
# ==========================================
personas = {
    "ESTP": {"title": "⚔️ 강력한 바바리안", "desc": "복잡한 서사보다는 즉각적인 피지컬 반응과 타격감을 사랑합니다. 실시간으로 변하는 전장에서 본능적으로 승리를 쟁취합니다.", "tags": ["Action", "Shooter", "PvP"]},
    "ESTJ": {"title": "🚩 용감한 기사", "desc": "체계적인 규칙과 효율을 중시합니다. 파티의 리더로서 최적의 전략을 구상하고 승리를 향해 전진하는 것을 즐깁니다.", "tags": ["Strategy", "Tactical", "Multiplayer"]},
    "ESFP": {"title": "🎉 유쾌한 바드", "desc": "게임은 다 같이 즐거워야 제맛! 화려한 이펙트와 가벼운 분위기 속에서 친구들과 소통하며 플레이하는 것을 선호합니다.", "tags": ["Casual", "Co-op", "Funny"]},
    "ESFJ": {"title": "🛡️ 든든한 프리스트", "desc": "자신보다 팀원의 생존을 먼저 챙기는 헌신적인 게이머입니다. 협동 플레이에서 자신의 역할이 빛날 때 큰 보람을 느낍니다.", "tags": ["Online Co-Op", "Support", "Casual"]},
    "ENTP": {"title": "🃏 혼돈의 네크로맨서", "desc": "정형화된 플레이는 거부합니다. 높은 자유도를 활용해 시스템의 허점을 찾거나 기발한 빌드를 설계하는 것을 즐깁니다.", "tags": ["Sandbox", "Physics", "Open World"]},
    "ENTJ": {"title": "👑 제국을 호령하는 군주", "desc": "거대한 제국을 세우고 경영하는 하드코어한 목표를 추구합니다. 치밀한 자원 관리와 정복 전쟁을 통해 정점에 서길 원합니다.", "tags": ["Simulation", "Strategy", "Management"]},
    "ENFP": {"title": "🗺️ 낭만적인 레인저", "desc": "새로운 지역을 발견하고 아름다운 풍경을 보는 것만으로도 행복합니다. 자유로운 탐험과 풍부한 상상력을 자극하는 세계를 좋아합니다.", "tags": ["Exploration", "Adventure", "Open World"]},
    "ENFJ": {"title": "⚖️ 평화를 수호하는 성기사", "desc": "세상을 구원하는 영웅 서사에 깊이 몰입합니다. 동료들과의 유대와 정의로운 선택이 강조되는 이야기를 사랑합니다.", "tags": ["Story Rich", "RPG", "Fantasy"]},
    "ISTP": {"title": "🗡️ 고독한 암살자", "desc": "말보다는 실력으로 증명합니다. 혼자서 묵묵히 어려운 보스의 패턴을 파훼하고 정교한 컨트롤로 승부하는 타입입니다.", "tags": ["Action", "Difficult", "Combat"]},
    "ISTJ": {"title": "⏱️ 완벽주의 수도사", "desc": "정해진 틀 안에서 오차 없는 플레이를 지향합니다. 반복되는 연습을 통해 기록을 단축하거나 복잡한 퍼즐을 푸는 데 재능이 있습니다.", "tags": ["Puzzle", "Linear", "Strategy"]},
    "ISFP": {"title": "🎨 자유로운 음유시인", "desc": "아름다운 음악과 감성적인 그래픽 속에서 힐링하는 것을 좋아합니다. 경쟁보다는 나만의 속도로 게임 속 삶을 즐깁니다.", "tags": ["Relaxing", "Cute", "Life Sim"]},
    "ISFJ": {"title": "🔨 성실한 장인", "desc": "노력한 만큼 쌓이는 결과물을 소중히 여깁니다. 차곡차곡 재료를 모아 장비를 만들거나 거점을 발전시키는 꾸준함이 강점입니다.", "tags": ["Crafting", "Building", "Simulation"]},
    "INTP": {"title": "🔮 심연을 탐구하는 마법사", "desc": "복잡한 수치와 시스템을 파고드는 지능형 게이머입니다. 매번 상황이 변하는 로그라이크나 심오한 세계관을 분석하는 것을 즐깁니다.", "tags": ["Rogue-like", "Sci-fi", "Turn-Based"]},
    "INTJ": {"title": "♟️ 전략적인 설계자", "desc": "피지컬보다는 뇌지컬! 수십 수 앞을 내다보는 전략을 설계합니다. 어둡고 진지한 분위기 속의 고도의 두뇌 싸움을 선호합니다.", "tags": ["Turn-Based Strategy", "Dark", "Puzzle"]},
    "INFP": {"title": "🌙 몽환적인 방랑자", "desc": "감성을 자극하는 독창적인 인디 게임을 사랑합니다. 여운이 남는 깊은 서사와 독특한 아트 스타일을 통해 감동을 얻습니다.", "tags": ["Atmospheric", "Indie", "Emotional"]},
    "INFJ": {"title": "📖 운명을 개척하는 예언자", "desc": "자신의 선택이 세계에 미치는 영향을 신중히 고민합니다. 철학적인 메시지나 캐릭터의 심리 묘사가 뛰어난 게임에 매료됩니다.", "tags": ["Choices Matter", "Mystery", "Story Rich"]}
}

# ==========================================
# 4. 질문 데이터 (12문항)
# ==========================================
questions = [
    # EI
    {"type": "EI", "q": "Q1. 주말 저녁, 각 잡고 게임을 켤 때 나의 기본 세팅은?", "options": [{"text": "디스코드 접속! 친구들 다 불러서 시끌벅적하게 파티 사냥", "score": "E", "tag": "Multiplayer"}, {"text": "랜덤 매칭을 돌려서 모르는 사람들과 가볍게 협동하기", "score": "E", "tag": "Online Co-Op"}, {"text": "알림은 적당히 켜두지만, 일단 혼자서 메인 퀘스트 진행", "score": "I", "tag": "Singleplayer"}, {"text": "모든 알림 오프. 오롯이 나만의 게임 세계로 깊게 빠져든다.", "score": "I", "tag": "Atmospheric"}]},
    {"type": "EI", "q": "Q2. 처음 보는 거대한 보스 몬스터를 마주쳤다!", "options": [{"text": "채팅으로 전략을 짜고 파티원들과 함께 레이드 뛴다.", "score": "E", "tag": "Co-op"}, {"text": "길드원이나 고인물에게 도와달라고 SOS 핑을 찍는다.", "score": "E", "tag": "Multiplayer"}, {"text": "혼자서 공략법을 검색해 보고 약점을 찾아낸다.", "score": "I", "tag": "Combat"}, {"text": "공략? 일단 혼자 1:1로 부딪혀보며 패턴을 외운다.", "score": "I", "tag": "Singleplayer"}]},
    {"type": "EI", "q": "Q3. 게임의 진정한 재미는 어디서 올까?", "options": [{"text": "남들과 경쟁해서 이기고 랭킹을 올렸을 때의 우월감", "score": "E", "tag": "PvP"}, {"text": "사람들과 소통하며 길드/클랜을 키워나가는 소속감", "score": "E", "tag": "Multiplayer"}, {"text": "아무도 못 찾은 숨겨진 요소나 맵을 탐험해 냈을 때의 성취감", "score": "I", "tag": "Exploration"}, {"text": "영화 같은 연출과 분위기를 오롯이 감상하며 느끼는 몰입감", "score": "I", "tag": "Atmospheric"}]},
    # NS
    {"type": "NS", "q": "Q4. 시작부터 튜토리얼과 스토리가 길게 이어진다면?", "options": [{"text": "모든 NPC에게 말을 걸어보며 숨겨진 세계관까지 파악한다.", "score": "N", "tag": "Story Rich"}, {"text": "대사를 꼼꼼히 읽으며 캐릭터들의 관계성을 이해하려 한다.", "score": "N", "tag": "Fantasy"}, {"text": "스토리는 요약본만 대충 읽고 조작법 위주로 빠르게 넘긴다.", "score": "S", "tag": "Action"}, {"text": "ESC 연타! 일단 직접 맞고 때려본다.", "score": "S", "tag": "Shooter"}]},
    {"type": "NS", "q": "Q5. 누굴 살릴지 결정하는 중요한 선택지가 등장했다!", "options": [{"text": "이 선택이 나비효과가 되어 엔딩에 미칠 영향을 고뇌한다.", "score": "N", "tag": "Choices Matter"}, {"text": "각 캐릭터의 서사와 감정선에 몰입하여 윤리적인 판단을 내린다.", "score": "N", "tag": "Drama"}, {"text": "어떤 선택이 당장 나에게 더 좋은 보상을 줄지 계산한다.", "score": "S", "tag": "Action RPG"}, {"text": "누굴 살려야 내 캐릭터 스탯이나 스킬 트리에 이득일지 본다.", "score": "S", "tag": "RPG"}]},
    {"type": "NS", "q": "Q6. 내 기억에 남는 '갓겜'의 핵심 요소는?", "options": [{"text": "끝난 뒤에도 여운이 길게 남는 깊은 떡밥.", "score": "N", "tag": "Mystery"}, {"text": "상상력을 자극하는 독특한 세계관과 아트 스타일.", "score": "N", "tag": "Sci-fi"}, {"text": "스트레스가 확 풀리는 찰진 타격감과 액션.", "score": "S", "tag": "Hack and Slash"}, {"text": "현실과 구분 안 가는 정교한 그래픽과 물리 엔진.", "score": "S", "tag": "Realistic"}]},
    # TF
    {"type": "TF", "q": "Q7. 보스전에서 계속 죽어서 1시간째 막혀있을 때 나의 반응은?", "options": [{"text": "원인을 분석하고 데미지를 계산해가며 최적화를 한다.", "score": "T", "tag": "Strategy"}, {"text": "내 피지컬을 탓하며 패턴을 피할 때까지 무한 재도전한다.", "score": "T", "tag": "Difficult"}, {"text": "아 스트레스 받아! 꺼버리고 힐링 게임이나 하러 간다.", "score": "F", "tag": "Casual"}, {"text": "본캐는 접어두고 예쁜 옷 입히기나 펫 꾸미기에 집중한다.", "score": "F", "tag": "Cute"}]},
    {"type": "TF", "q": "Q8. 나의 뇌를 더 자극하는 게임 요소는?", "options": [{"text": "한정된 자원을 효율적으로 분배하고 관리하는 것.", "score": "T", "tag": "Management"}, {"text": "내 턴에 상대의 수를 예측하며 치밀한 전략을 짜는 것.", "score": "T", "tag": "Turn-Based Strategy"}, {"text": "마음이 편안해지는 BGM과 따뜻한 그래픽.", "score": "F", "tag": "Great Soundtrack"}, {"text": "빵 터지는 유머 코드와 개그 캐릭터들.", "score": "F", "tag": "Funny"}]},
    {"type": "TF", "q": "Q9. 게임의 난이도를 자유롭게 설정할 수 있다면?", "options": [{"text": "최고 난이도! 실패의 쓴맛이 있어야 도파민도 크다.", "score": "T", "tag": "Survival Horror"}, {"text": "어려움. 적당히 매운맛이 있어야 성취감이 든다.", "score": "T", "tag": "Difficult"}, {"text": "보통. 제작자가 의도한 표준적인 재미면 충분하다.", "score": "F", "tag": "Colorful"}, {"text": "쉬움. 현실도 힘든데 게임은 그저 평화롭게!", "score": "F", "tag": "Relaxing"}]},
    # PJ
    {"type": "PJ", "q": "Q10. 오픈월드에 뚝 떨어졌다. 나의 첫 행동은?", "options": [{"text": "눈에 띄는 제일 높은 산봉우리부터 무작정 등반해 본다.", "score": "P", "tag": "Open World"}, {"text": "보이는 서브 퀘스트는 일단 목적 없이 다 수락해 둔다.", "score": "P", "tag": "Exploration"}, {"text": "전체 맵을 열고 가장 효율적인 동선 루트를 계산한다.", "score": "J", "tag": "Strategy"}, {"text": "다른 길로 새지 않고 메인 퀘스트 마커만 곧장 따라간다.", "score": "J", "tag": "Linear"}]},
    {"type": "PJ", "q": "Q11. 내가 더 선호하는 게임의 흐름은?", "options": [{"text": "매번 맵과 아이템이 랜덤으로 바뀌는 예측 불허의 상황.", "score": "P", "tag": "Rogue-like"}, {"text": "정해진 목적 없이 내 마음대로 창조하는 샌드박스.", "score": "P", "tag": "Sandbox"}, {"text": "정해진 룰 안에서 톱니바퀴처럼 딱 떨어지는 정답 찾기.", "score": "J", "tag": "Turn-Based"}, {"text": "머리를 써서 정확한 순서대로 기믹을 풀어내는 퍼즐.", "score": "J", "tag": "Puzzle"}]},
    {"type": "PJ", "q": "Q12. 하우징(집 꾸미기) 시스템이 있다면?", "options": [{"text": "비효율적이어도 낭만 가득한 컨셉 저택을 짓는다.", "score": "P", "tag": "Building"}, {"text": "일단 이것저것 설치해 보면서 즉흥적으로 확장한다.", "score": "P", "tag": "Crafting"}, {"text": "제작대, 보관함 등을 동선 낭비 없게 배치한다.", "score": "J", "tag": "Management"}, {"text": "아이템 종류별로 창고 칸을 엄격하게 분류한다.", "score": "J", "tag": "Base-Building"}]}
]

# ==========================================
# 5. 세션 상태 관리
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'test_completed' not in st.session_state:
    st.session_state['test_completed'] = False
if 'current_q_idx' not in st.session_state:
    st.session_state['current_q_idx'] = 0 
if 'user_answers' not in st.session_state:
    st.session_state['user_answers'] = {} 

# ==========================================
# 6. 화면 구성: 로그인
# ==========================================
if not st.session_state['logged_in']:
    # [수정됨] image 폴더 경로 지정
    st.image("image/start_bg.jpg", use_container_width=True)
    st.title("🎮 게임 성향 테스트")
    st.info("🔥 현재까지 많은 게이머가 자신의 '진짜 직업'을 찾았습니다!")
    
    with st.form("login_form"):
        nickname = st.text_input("사용자 닉네임", placeholder="예: 홍길동")
        if st.form_submit_button("모험 시작하기 🚀"):
            if nickname:
                st.session_state['logged_in'] = True
                st.session_state['user_nickname'] = nickname
                st.rerun()

# ==========================================
# 7. 화면 구성: 1문제씩 보여주는 퀴즈
# ==========================================
elif not st.session_state['test_completed']:
    idx = st.session_state['current_q_idx']
    q_data = questions[idx]
    
    st.progress((idx) / len(questions))
    st.caption(f"진행 상황: {idx + 1} / {len(questions)}")
    
    st.markdown(f"<h3 style='text-align: center;'>{q_data['q']}</h3>", unsafe_allow_html=True)
    st.write("") 
    
    for i, opt in enumerate(q_data['options']):
        is_sel = (st.session_state['user_answers'].get(idx) == i)
        if st.button(opt['text'], key=f"q{idx}o{i}", type="primary" if is_sel else "secondary", use_container_width=True):
            st.session_state['user_answers'][idx] = i
            st.rerun()

    st.markdown("---")
    c1, _, c3 = st.columns([1, 1, 1])
    with c1:
        if idx > 0 and st.button("⬅️ 이전 질문"):
            st.session_state['current_q_idx'] -= 1
            st.rerun()
    with c3:
        if idx in st.session_state['user_answers']:
            if idx < len(questions) - 1:
                if st.button("다음 질문 ➡️"):
                    st.session_state['current_q_idx'] += 1
                    st.rerun()
            else:
                if st.button("결과 확인하기 🚀", type="primary"):
                    st.session_state['test_completed'] = True
                    st.rerun()

# ==========================================
# 8. 화면 구성: 결과 분석 및 추천
# ==========================================
else:
    st.balloons()
    scores = {"E": 0, "I": 0, "N": 0, "S": 0, "T": 0, "F": 0, "P": 0, "J": 0}
    final_tags = []
    for q_idx, sel_idx in st.session_state['user_answers'].items():
        opt = questions[q_idx]['options'][sel_idx]
        scores[opt['score']] += 1
        final_tags.append(opt['tag'])

    res = ("E" if scores["E"] >= scores["I"] else "I") + \
          ("N" if scores["N"] >= scores["S"] else "S") + \
          ("T" if scores["T"] >= scores["F"] else "F") + \
          ("P" if scores["P"] >= scores["J"] else "J")

    p = personas.get(res, personas["ISTP"])
    
    c1, c2 = st.columns([1, 2])
    with c1:
        # [수정됨] image 폴더 내의 캐릭터 이미지 불러오기
        file_name = f"image/{res.lower()}.png"
        
        try:
            st.image(file_name, use_container_width=True)
        except Exception:
            # 예외 처리: 파일이 없을 경우 DiceBear API로 임시 아바타 생성
            st.warning("이미지를 찾을 수 없어 임시 아바타를 표시합니다.")
            st.image(f"https://api.dicebear.com/7.x/adventurer/svg?seed={res}&backgroundColor=c0aede", use_container_width=True)
        
    with c2:
        st.markdown(f"### {st.session_state['user_nickname']}님은...")
        st.header(p['title'])
        st.markdown(f"<div class='result-box'>{p['desc']}</div>", unsafe_allow_html=True)

    st.subheader("🎁 당신을 위한 강력 추천 스팀 게임")
    
    # 추천 알고리즘
    search_tags = list(set(final_tags + p['tags']))
    games_df['Match_Score'] = games_df['Tags'].apply(lambda x: sum(1 for t in search_tags if t in str(x)))
    
    reco = games_df.sort_values(by=['Match_Score', 'Positive'], ascending=[False, False]).head(10)
    
    cols = st.columns(3)
    for i, row in reco.sample(n=min(3, len(reco))).reset_index(drop=True).iterrows():
        with cols[i]:
            # 스팀 이미지 로드
            st.image(f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{int(row['AppID'])}/header.jpg", use_container_width=True)
            st.markdown(f"**{row['Name']}**")
            st.caption(f"장르: {row['Tags']}")
            st.link_button("🎮 스팀 상점", f"https://store.steampowered.com/app/{int(row['AppID'])}", use_container_width=True)

    if st.button("다시 테스트하기 🔄", use_container_width=True):
        st.session_state.clear()
        st.rerun()