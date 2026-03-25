# CLAUDE.md — 토트넘 강등 저지 게임

이 파일은 Claude Code가 **매 세션 시작 시 자동으로 읽는** 프로젝트 기억입니다.
**모든 세션은 반드시 이 파일을 먼저 읽고 시작하세요.**

---

## 프로젝트 개요

- **게임명**: 토트넘 강등 저지 — 당신이 감독이다
- **목적**: Streamlit + OpenAI API를 활용한 텍스트 기반 풋볼 매니저 게임 (Light 버전)
- **실행**: `streamlit run app.py`
- **테스트**: `python -m pytest tests/ -v`

## 기술 스택

- Python 3.11+
- Streamlit 1.32+
- OpenAI API (`gpt-4o-mini`, STT: `whisper-1`, TTS: `tts-1`)
- SpeechRecognition + PyAudio (로컬 마이크 STT 폴백)
- pytest (단위 테스트)
- Git (세션별 커밋 필수)

## Light 버전 스코프 (확정)

> **Light 버전은 아래 항목만 구현한다. 이 외는 추가하지 않는다.**

| 포함 | 제외 |
|------|------|
| 경기 에이전트 (내러티브 생성) | 교체 시스템 |
| 훈련 에이전트 (내러티브 생성) | RAG 실제 구현 |
| 강등 확률 에이전트 (수학 계산) | 기적 엔딩 |
| 수치 기반 시뮬레이터 | 난이도 선택 |
| 경쟁팀 랜덤 결과 | 경쟁 상대팀에 따른 영향 |
| **STT 하프타임 스피치** (음성 입력 → 텍스트 → 감정 분석 → 수치 반영) | 경기 중 교체 UI |
| **TTS 라커룸 스피치** (경기 후 AI 스피치 텍스트 생성 → TTS 음성 재생) | |

---

## 절대 규칙 — 어떤 세션에서도 위반 금지

1. **state.py의 GameState 스키마는 변경 금지** (필드 추가/삭제/타입 변경 모두 금지)
   - 변경이 필요하면 반드시 사람에게 먼저 확인받을 것
2. **함수 시그니처 유지**: 다른 모듈이 호출하는 함수의 파라미터/반환 타입 변경 금지
3. **범위 준수**: 요청받은 파일만 수정. 다른 파일은 읽기만 할 것
4. **테스트 필수**: 새 함수 추가 시 반드시 단위 테스트 포함
5. **수치 범위 강제**: 모든 0~100 수치는 `max(0, min(100, value))` 클리핑 적용
6. **LLM 호출 위치**: `agents/` 폴더 파일에서만. `simulator.py`, `training.py`, `state.py`는 LLM 호출 금지
7. **Git 커밋 필수**: 세션 종료 전 반드시 커밋. 커밋 메시지 형식: `[S{번호}] {작업 내용 한 줄}`

---

## 파일 역할 지도

```
app.py                     — Streamlit UI 전용. 비즈니스 로직 없음.
state.py                   — GameState 스키마 + 저장/불러오기만. LLM 호출 없음.
simulator.py               — 수치 기반 승률 계산 + 경기 시뮬레이션. LLM 호출 없음.
training.py                — 훈련 효과 계산. LLM 호출 없음.
agents/match_agent.py      — 경기 내러티브 생성 (OpenAI API 호출)
agents/training_agent.py   — 훈련 내러티브 생성 (OpenAI API 호출)
agents/relegation_agent.py — 강등 확률 계산 + 분석 텍스트 (Analysis Tool + OpenAI API 호출) [S3 구현 예정]
agents/voice_agent.py      — STT 입력 처리 + 감정/강도 분석 + TTS 라커룸 스피치 생성/재생 [S4 구현 예정]
rag/retriever.py           — RAG 스텁. Light 버전에서는 빈 결과만 반환. 실제 구현 금지.
tests/test_simulator.py    — 시뮬레이터 단위 테스트
tests/test_relegation.py   — 강등 에이전트 단위 테스트 [S3 추가 예정]
tests/test_voice.py        — 음성 에이전트 단위 테스트 [S4 추가 예정]
```

---

## GameState 스키마 (기준 — 절대 변경 금지)

```python
@dataclass
class GameState:
    team_stats: dict = {
        "condition": 70,              # 0~100
        "morale": 50,                 # 0~100
        "tactical_understanding": 50, # 0~100
        "cohesion": 60,               # 0~100
        "fan_sentiment": 50,          # 0~100
        "owner_trust": 60,            # 0~100 — 0이 되면 sacked 엔딩
        "press_level": 5,             # 1~10
    }
    captain_stats: dict = {
        "condition": 80, "morale": 60, "manager_relation": 70,
        "press_sentiment": 75, "leadership": 85,
        "professionalism": 90, "loyalty": 80,
    }
    vice_captain_stats: dict = {      # captain_stats와 동일 구조
        "condition": 75, "morale": 58, "manager_relation": 65,
        "press_sentiment": 70, "leadership": 78,
        "professionalism": 85, "loyalty": 75,
    }
    remain_round: int = 7             # 잔여 경기 수 ← current_round 아님. 절대 혼용 금지.
    points: int = 37                  # 현재 승점
    position: int = 16                # 현재 순위
    match_history: list = []          # 경기 기록
    training_buff: float = 0.0        # 다음 경기 승률 보정
    training_buff_expires: int = 0    # 몇 경기 후 만료
    game_over: bool = False
    ending_type: str = ""             # "survival" | "relegation" | "sacked"
    mode: str = "normal"
    consecutive_losses: int = 0
    manager_name: str = "감독"
    rival_teams: dict = {
        "Nottingham Forest": {"points": 32, "remaining_matches": 7, "goal_difference": -12},
        "West Ham":          {"points": 29, "remaining_matches": 7, "goal_difference": -21},
        "Leeds United":      {"points": 33, "remaining_matches": 7, "goal_difference": -11},
        "Burnley":           {"points": 19, "remaining_matches": 7, "goal_difference": -28},
        "Wolves":            {"points": 17, "remaining_matches": 7, "goal_difference": -30},
    }
    schedule: list = [
        {"round": 32, "opponent": "Sunderland",  "is_home": False, "opponent_strength": 6, "date": "2026-04-11"},
        {"round": 33, "opponent": "Brighton",    "is_home": True,  "opponent_strength": 7, "date": "2026-04-18"},
        {"round": 34, "opponent": "Wolves",      "is_home": False, "opponent_strength": 5, "date": "2026-04-25"},
        {"round": 35, "opponent": "Aston Villa", "is_home": False, "opponent_strength": 8, "date": "2026-05-02"},
        {"round": 36, "opponent": "Leeds",       "is_home": True,  "opponent_strength": 6, "date": "2026-05-09"},
        {"round": 37, "opponent": "Chelsea",     "is_home": False, "opponent_strength": 9, "date": "2026-05-17"},
        {"round": 38, "opponent": "Everton",     "is_home": True,  "opponent_strength": 7, "date": "2026-05-24"},
    ]
```

---

## 수치 밸런스 테이블 (확정값 — 변경 시 주석 남길 것)

### 포메이션별 승률 보정

| 포메이션 | base_win_bonus | condition_weight | morale_weight | tactical_weight |
|---------|---------------|-----------------|--------------|----------------|
| 4-3-3 (공격형) | +0.02 | 0.40 | 0.35 | 0.25 |
| 4-5-1 (균형형) | 0.00 | 0.33 | 0.33 | 0.34 |
| 3-4-3 (전방압박) | +0.03 | 0.50 | 0.30 | 0.20 |

> `opponent_strength`(1~10)를 `difficulty = opponent_strength / 10.0`으로 변환해 승률 계산에 사용

### 하프타임 스피치 효과 — 선택지 방식

| 스피치 | morale | cohesion | tactical | manager_relation | win_rate_bonus |
|--------|--------|----------|---------|-----------------|----------------|
| 강한 동기부여 | +12 | +5 | 0 | +3 | +0.06 |
| 전술 수정 | +4 | +2 | +5 | +2 | +0.04 |
| 질책 | -3 | -4 | 0 | -8 | +0.02 |
| 침착하게 | +2 | +3 | 0 | +1 | +0.01 |

### 하프타임 스피치 효과 — STT 음성 입력 방식 (S4 구현)

> 음성 입력 시 선택지 방식 대신 아래 로직을 적용한다.
> LLM이 발화 텍스트를 분석해 `intensity`(강도)와 `sentiment`(감정)를 판정.

| intensity | win_rate_bonus | morale_delta | 발동 조건 예시 |
|-----------|---------------|-------------|-------------|
| high_positive | +0.10 | +15 | 열정적·긍정적 ("우리는 할 수 있어!", "포기하지 마!") |
| mid_positive | +0.06 | +10 | 일반 격려 |
| tactical | +0.04 | +4 | 전술 지시 키워드 포함 ("수비 라인 올려", "역습 집중") |
| negative | +0.01 | -5 | 부정적·질책 ("왜 이렇게 못해", "실망이야") |

> **음성 직접 입력 보너스**: 선택지 대비 `win_rate_bonus +0.02` 추가 적용 (몰입감 가산점)
> 예시: `high_positive` + 음성입력 = win_rate_bonus **0.12**

### 경기 후 스피치 효과 (라커룸 — TTS 재생 후 선택)

| 스피치 | morale | cohesion | owner_trust | manager_relation |
|--------|--------|----------|-------------|-----------------|
| 칭찬 | +10 | +5 | +3 | 0 |
| 격려 | +6 | +3 | +1 | 0 |
| 질책 | -8 | -5 | -2 | -10 |

> TTS 라커룸 스피치 흐름: 경기 종료 → LLM이 결과 기반 스피치 텍스트 생성 → TTS 음성 재생
> → 감독이 [칭찬/격려/질책] 선택 → 위 수치 반영 → 기자회견으로 이동

### 기자회견 효과

| 선택 | fan_sentiment | owner_trust | press_sentiment(주장) |
|------|--------------|-------------|----------------------|
| 신중하게 | +3 | +2 | +5 |
| 공격적으로 | +8 | -10 | -5 |
| 유머로 | +10 | -5 | +8 |

### 훈련 효과

| 훈련 | condition | tactical | morale | training_buff | 지속 |
|------|-----------|---------|--------|---------------|------|
| 회복 훈련 | +14 | 0 | +3 | 0 | - |
| 체력 훈련 | +5 | 0 | 0 | +0.02 | 1경기 |
| 전술 훈련 | -3 | +8 | +1 | +0.03 | 2경기 |

### 경기 결과 → 수치 변화

| 결과 | morale | owner_trust | fan_sentiment | consecutive_losses | condition |
|------|--------|-------------|---------------|--------------------|---------|
| 승리 | +8 | +5 | +7 | 초기화(0) | -8 |
| 무승부 | +1 | -2 | 0 | 초기화(0) | -8 |
| 패배 | -10 | -8 | -5 | +1 | -8 |

---

## 엔딩 조건 (확정 — 3가지)

| 엔딩 | 조건 | 설명 |
|------|------|------|
| `survival` | remain_round == 0 AND position ≤ 17 | 강등 탈출 성공 (14위 이하도 동일) |
| `relegation` | remain_round == 0 AND position ≥ 18, 또는 수학적 강등 확정 | 강등 |
| `sacked` | owner_trust ≤ 0 (즉시, 잔여경기 무관) | 경질 |

> `mid_table` 엔딩 없음. position ≤ 14도 `survival`로 처리.

---

## STT 설계 (S4에서 voice_agent.py로 구현)

### 라이브러리 및 우선순위

```
STT 우선순위:
  1순위 — OpenAI Whisper API (whisper-1)
          client.audio.transcriptions.create(file=f, model='whisper-1')
  2순위 — SpeechRecognition + PyAudio (로컬 마이크 실시간)
          recognizer.recognize_google(audio, language='ko-KR')
  폴백  — 텍스트 직접 입력 (API 키 없거나 마이크 없을 때)
```

### voice_agent.py STT 인터페이스 (S4에서 구현)

```python
def transcribe_speech(audio_file_path: str) -> str:
    """STT: 오디오 파일 → 텍스트. 실패 시 빈 문자열 반환."""

def analyze_speech_intensity(text: str) -> dict:
    """
    LLM으로 발화 텍스트 강도/감정 분석.
    Returns: {
        "intensity": str,        # "high_positive"|"mid_positive"|"tactical"|"negative"
        "win_rate_bonus": float,
        "morale_delta": int,
        "summary": str,          # 분석 결과 한 줄 (UI 표시용)
    }
    """

def record_microphone(timeout: int = 10) -> str:
    """실시간 마이크 녹음 → 임시 wav 저장. 실패 시 빈 문자열 반환."""
```

### Streamlit 하프타임 STT 흐름 (app.py S7에서 추가)

```
하프타임 화면:
  [🎙️ 음성으로 스피치하기] 클릭
    → st.file_uploader() 또는 st.audio_input()으로 오디오 수집
    → voice_agent.transcribe_speech(audio) 호출
    → voice_agent.analyze_speech_intensity(text) 호출
    → 분석 결과(intensity, 예상 보너스) UI 표시
    → [적용] 버튼 → 수치 반영 후 후반전 시뮬레이션
  [📝 텍스트로 입력] 클릭  ← 폴백
    → 기존 선택지 4가지 방식으로 진행
```

---

## TTS 설계 (S4에서 voice_agent.py로 구현)

### 라이브러리 및 우선순위

```
TTS 우선순위:
  1순위 — OpenAI TTS API (tts-1)
          client.audio.speech.create(model="tts-1", voice="onyx", input=text)
          → 반환된 mp3 bytes를 st.audio()로 재생
  2순위 — 브라우저 Web Speech API (st.components.v1.html 인라인 JS)
          → speechSynthesis.speak(new SpeechSynthesisUtterance(text))
  폴백  — 텍스트만 화면에 표시 (음성 재생 없음)
```

### voice_agent.py TTS 인터페이스 (S4에서 구현)

```python
def generate_locker_room_speech(gs: GameState, result: str) -> str:
    """
    경기 결과 기반 라커룸 스피치 텍스트 생성 (LLM 호출).
    result: "win" | "draw" | "loss"
    Context: gs.team_stats(morale, cohesion), gs.consecutive_losses, gs.points 참조
    Returns: 감독의 라커룸 스피치 텍스트 (한국어, 3~5문장)
    Prompt 방향:
      win  → 칭찬 + 다음 경기 경계
      draw → 아쉬움 + 집중력 강조
      loss → 침착한 격려 또는 질책 (consecutive_losses >= 3이면 강도 높임)
    """

def speak_text(text: str) -> bytes | None:
    """
    TTS: 텍스트 → mp3 bytes (OpenAI tts-1, voice='onyx').
    실패(API 키 없음 등) 시 None 반환 → 폴백 처리는 app.py에서.
    """
```

### Streamlit 라커룸 TTS 흐름 (app.py S7에서 추가)

```
경기 결과 화면 (match_agent 내러티브 표시 직후):
  → voice_agent.generate_locker_room_speech(gs, result) 호출 (LLM)
  → 스피치 텍스트 st.info() 박스에 표시
  → voice_agent.speak_text(text) 호출
    성공 → st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    실패 → Web Speech API 폴백 (st.components.v1.html)
           실패 → 텍스트만 표시
  → [🏆 칭찬] [💪 격려] [😤 질책] 버튼 → 수치 반영
  → [건너뛰기] → 스피치 없이 선택지 바로 표시
  → 선택 완료 후 기자회견 화면으로 이동
```

### TTS 프롬프트 가이드라인

```
시스템 프롬프트:
  "당신은 토트넘 감독입니다. 경기 직후 라커룸에서 선수단에게 짧고 강렬한 스피치를 합니다.
   한국어로, 3~5문장, 과장 없이 현실적인 감독 말투로 작성하세요."

유저 메시지 예시 (win):
  f"방금 {opponent}를 상대로 승리했습니다. 현재 승점 {points}점, 잔여 {remain_round}경기.
   팀 사기 {morale}/100. 라커룸 스피치를 작성하세요."
```

---

## 강등 확률 계산 로직 (S3에서 relegation_agent.py로 구현)

현재 `relegation_probability()`는 단순 추정값.
S3에서 **Claude의 Analysis Tool(JS 계산기)** 을 사용해 잔여 경기 승점 시뮬레이션을 수행하는 방식으로 교체.

**계산 방식:**
```
Claude Analysis Tool(JS)이 아래를 계산:
  1. 토트넘 최대 가능 승점: points + remain_round * 3
  2. 각 경쟁팀의 최대 가능 승점: rival.points + rival.remaining_matches * 3
  3. 강등선 추정: 경쟁팀 현재 승점 분포를 바탕으로 17위/18위 경계 동적 계산
  4. 잔여 경기 전체 조합(win/draw/loss)에 대한 승점 시나리오 열거
  5. 강등 확률 = 토트넘이 18위 이하로 끝나는 시나리오 수 / 전체 시나리오 수
     (경쟁팀은 각각 기댓값 기준으로 처리: 승 28% * 3 + 무 27% * 1 + 패 45% * 0)
```

**relegation_agent.py 인터페이스:**
```python
def calculate_relegation_probability(gs: GameState) -> dict:
    """
    Claude Analysis Tool(JS)으로 승점 시뮬레이션 수행.
    Returns: {
        "probability": float,              # 0.0~1.0
        "max_possible_pts": int,
        "safe_line_estimate": int,
        "analysis": str,                   # LLM 생성 한국어 2~3문장
        "is_mathematically_safe": bool,    # 져도 잔류 확정
        "is_mathematically_relegated": bool, # 이겨도 강등 확정
    }
    """
```

---

## 세션별 구현 범위 (확정)

| 세션 | 파일 | 작업 내용 | 상태 |
|------|------|---------|------|
| S1 | `state.py` | GameState 스키마 + 저장/불러오기 | ✅ 완료 |
| S2 | `simulator.py`, `training.py`, `tests/test_simulator.py` | 수치 시뮬레이터 + 테스트 | ✅ 완료 |
| S3 | `agents/relegation_agent.py`, `tests/test_relegation.py` | 강등 확률 에이전트 (Analysis Tool JS 계산 + LLM) | ⬜ 다음 |
| S4 | `agents/voice_agent.py`, `tests/test_voice.py` | STT 음성 에이전트 + TTS 라커룸 스피치 생성/재생 | ⬜ |
| S5 | `agents/match_agent.py` | 경기 에이전트 검증 | ✅ 완료 (S2 선구현) |
| S6 | `agents/training_agent.py` | 훈련 에이전트 검증 | ✅ 완료 (S2 선구현) |
| S7 | `app.py` 수정 | relegation_agent + voice_agent UI 연결, STT 하프타임 + TTS 라커룸 흐름 추가 | ⬜ S3·S4 후 진행 |
| S8 | `tests/` 전체 | 통합 테스트 + 밸런스 검증 | ⬜ |
| S9 | `README.md` | 실행 방법 + 스크린샷 | ⬜ |

---

## 현재 진행 상황

> **이 섹션은 매 세션 종료 시 업데이트할 것**

- [x] S1: state.py GameState 스키마 확정
- [x] S2: simulator.py + training.py + agents(match/training) + app.py 선구현 + 테스트
- [ ] S3: agents/relegation_agent.py — **다음 세션 목표**
- [ ] S4: agents/voice_agent.py (STT + TTS)
- [ ] S5: agents/match_agent.py 검증
- [ ] S7: app.py 음성 흐름 + relegation_agent 연결
- [ ] S8: 통합 테스트
- [ ] S9: README.md

**현재 작업 파일**: 없음 (S2 완료, S3 대기)

**알려진 이슈**:
- `relegation_probability()` in simulator.py → 단순 추정값. S3에서 교체 예정
- `check_ending()` SAFE_LINE=40 하드코딩 → S3 이후 교체 예정
- app.py 하프타임 화면 → 선택지 방식만 구현. S7에서 STT 흐름 추가 예정
- app.py 경기 후 화면 → TTS 라커룸 스피치 없음. S7에서 추가 예정
- `remain_round` 필드명 주의 (구버전 `current_round` 잔재 있을 수 있음)
- simulator.py의 `difficulty` 계산: `opponent_strength / 10.0` 방식으로 교체 필요

**다음 세션(S3) 작업 목표**:
1. `agents/relegation_agent.py` 신규 생성
2. `tests/test_relegation.py` 작성
3. `python -m pytest tests/test_relegation.py -v` 통과 확인
4. CLAUDE.md S3 체크박스 완료 표시
5. `git add -A && git commit -m "[S3] relegation_agent Analysis Tool 승점 시뮬레이션 구현"`

---

## Git 규칙

```bash
# 세션 시작 시 — 직전 세션 커밋 상태 확인 (필수)
git log --oneline -5

# 세션 종료 시 — 반드시 커밋
git add -A
git commit -m "[S{번호}] {작업 내용 한 줄 요약}"

# 커밋 메시지 예시
[S3] relegation_agent Analysis Tool 승점 시뮬레이션 구현
[S4] voice_agent STT + TTS 라커룸 스피치 구현
[S5] match_agent 검증 완료
[S7] app.py relegation_agent + STT 하프타임 + TTS 라커룸 흐름 연결
[S8] 통합 테스트 + 밸런스 검증
[S9] README.md 작성

# 브랜치: main 단일 브랜치 사용
```

---

## 자주 쓰는 명령어

```bash
# 앱 실행
OPENAI_API_KEY=sk-... streamlit run app.py

# API 키 없이 실행 (STT/LLM/TTS 비활성, 수치만)
streamlit run app.py

# 전체 테스트
python -m pytest tests/ -v

# 특정 파일 테스트
python -m pytest tests/test_simulator.py -v

# Git 상태 확인
git log --oneline -5
git status
```

---

## 세션 시작 체크리스트

1. 이 CLAUDE.md 읽기 (자동)
2. `git log --oneline -5` 실행 → 직전 세션 커밋 확인
3. "현재 진행 상황" 섹션 확인
4. 해당 세션 대상 파일만 `view`로 열기
5. "이번 세션에서 할 일" 한 줄 요약 출력 후 작업 시작

## 세션 종료 체크리스트

1. 구현 파일 저장 확인
2. `python -m pytest tests/ -v` 실행 → 결과 확인
3. CLAUDE.md 업데이트 (체크박스, 알려진 이슈, 다음 세션 목표)
4. `git add -A && git commit -m "[S{번호}] {내용}"` 실행
