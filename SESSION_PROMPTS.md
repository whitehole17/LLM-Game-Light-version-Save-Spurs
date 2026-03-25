# 세션별 추천 프롬프트 — 토트넘 강등 저지 게임

> 각 세션 시작 시 아래 프롬프트를 **그대로 복사**해서 Claude Code에 붙여넣으세요.
> 모든 프롬프트는 `CLAUDE.md 읽기 → git 확인 → 작업 → 테스트 → 커밋` 순서를 따릅니다.

---

## ✅ S1 — state.py

CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 커밋 이력 보여줘.

S1 신규 작업이야. state.py 파일이 없으므로 CLAUDE.md 스키마를 기준으로 새로 작성해줘.

구현 항목:
1. GameState 데이터클래스 — CLAUDE.md "GameState 스키마" 섹션과 100% 동일하게 구현
   - 필드명: remain_round (current_round 절대 금지)
   - rival_teams: dict 타입 (list 아님)
   - schedule: 각 항목에 round, opponent, is_home, opponent_strength, date 포함
   - ending_type 기본값: "" (허용값: "survival"|"relegation"|"sacked")
2. clip(value: float, lo: float = 0, hi: float = 100) -> float
   - max(lo, min(hi, value)) 클리핑
3. save_state(gs: GameState, path: str = "save.json") -> None
   - dataclasses.asdict() 사용, json.dump()로 저장
4. load_state(path: str = "save.json") -> GameState
   - json.load() 후 GameState(**data)로 복원
5. new_game(manager_name: str = "감독") -> GameState
   - 기본값 GameState 생성 후 manager_name만 교체

규칙:
- LLM 호출 금지 (절대 규칙 6번)
- import: dataclasses, json, copy, typing만 허용
- 모든 수치 기본값은 CLAUDE.md 스키마와 정확히 일치

완료 후:
  git add state.py && git commit -m "[S1] state.py GameState 스키마 구현"

---

## ✅ S2 — simulator.py + training.py (완료)

재작업이 필요한 경우에만 사용.

```
CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 커밋 이력 보여줘.

S2 재검토 작업이야. 아래 파일들을 순서대로 열어서 확인해줘:

1. simulator.py
   - difficulty 계산이 opponent_strength / 10.0 방식인지
     (기존에 "difficulty" 필드 직접 참조하면 opponent_strength / 10.0으로 교체)
   - remain_round를 쓰는 곳에서 current_round를 쓰고 있으면 전부 수정
   - CLAUDE.md 수치 밸런스 테이블과 모든 delta 값이 일치하는지
   - rival_teams가 dict 타입임을 감안한 _simulate_rivals() 로직인지

2. training.py
   - 훈련 효과 테이블과 값이 일치하는지

3. tests/test_simulator.py
   - remain_round 필드명을 올바르게 쓰고 있는지

불일치 항목은 CLAUDE.md 기준으로 수정하고 테스트 실행해줘:
  python -m pytest tests/test_simulator.py -v

완료 후:
  git add -A && git commit -m "[S2] simulator.py remain_round + opponent_strength 수정"
```

---

## ⬜ S3 — agents/relegation_agent.py (다음 세션)

```
CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 직전 세션 커밋을 확인해줘.

S3 작업이야. agents/relegation_agent.py를 새로 만들어줘.

구현 요구사항:

1. calculate_relegation_probability(gs: GameState) -> dict 함수 구현
   반환값은 CLAUDE.md의 인터페이스 명세를 그대로 따를 것:
   {
     "probability": float,
     "max_possible_pts": int,
     "safe_line_estimate": int,
     "analysis": str,
     "is_mathematically_safe": bool,
     "is_mathematically_relegated": bool,
   }

2. Claude의 Analysis Tool(JS 계산기)을 사용하여 잔여 경기 승점 시뮬레이션 수행
   - JS 코드로 아래를 계산:
     · 토트넘 최대 가능 승점: gs.points + gs.remain_round * 3
     · 각 경쟁팀 최대 가능 승점: rival.points + rival.remaining_matches * 3
     · 강등선 추정: 경쟁팀 현재 승점 분포에서 17위/18위 경계 동적 계산
     · 잔여 경기 시나리오 열거(win/draw/loss 조합)로 토트넘 승점 분포 계산
     · 경쟁팀은 기댓값 기준 처리: 승 28%×3 + 무 27%×1 + 패 45%×0 = 1.11점/경기
     · probability = 토트넘이 18위 이하로 끝나는 시나리오 수 / 전체 시나리오 수

3. is_mathematically_relegated
   = max_possible_pts < 경쟁팀 중 18위권 팀의 최솟값 현재 승점일 때 True

4. is_mathematically_safe
   = 현재 points > 모든 경쟁팀의 max_possible_pts 일 때 True

5. analysis: OpenAI API로 한국어 2~3문장 생성
   - API 키 없을 때는 빈 문자열 반환 (예외 금지)
   - 프롬프트: 강등 확률, 잔여 경기, 경쟁팀 현황을 바탕으로 냉철하게 분석

그리고 tests/test_relegation.py도 만들어줘:
- probability가 0.0~1.0 범위인지
- is_mathematically_relegated: remain_round=0, position=19일 때 True인지
- is_mathematically_safe: points=100일 때 True인지
- 함수가 에러 없이 실행되는지 (LLM 호출 mock 처리)
- rival_teams dict 타입으로 올바르게 순회하는지

테스트 실행:
  python -m pytest tests/test_relegation.py -v

완료 후:
  CLAUDE.md S3 체크박스 완료 표시, 다음 세션 목표를 S4로 업데이트
  git add -A && git commit -m "[S3] relegation_agent Analysis Tool 승점 시뮬레이션 구현"
```

---

## ⬜ S4 — agents/voice_agent.py (STT)

```
CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 S3 커밋이 있는지 확인해줘.
S3 커밋이 없으면 작업을 시작하지 말고 "S3 먼저 완료해주세요"라고 알려줘.

S4 작업이야. agents/voice_agent.py를 새로 만들어줘.

구현 요구사항:

1. transcribe_speech(audio_file_path: str) -> str
   - OpenAI Whisper API 우선 시도
     client.audio.transcriptions.create(file=f, model='whisper-1')
   - 실패 또는 API 키 없으면 SpeechRecognition 폴백
   - 둘 다 실패하면 빈 문자열 반환 (예외 밖으로 던지지 말 것)

2. analyze_speech_intensity(text: str) -> dict
   - OpenAI API로 발화 텍스트 감정/강도 분석
   - 반환값: {"intensity": str, "win_rate_bonus": float, "morale_delta": int, "summary": str}
   - intensity 분류 기준은 CLAUDE.md STT 수치 테이블 그대로 적용
   - 음성 입력 보너스 +0.02는 이 함수에서 적용하지 않음
     (app.py에서 is_voice=True일 때 +0.02 추가하는 방식으로 분리)
   - API 키 없으면 text 길이/키워드 기반 규칙으로 폴백:
     "포기" "할 수 있" "가자" 등 키워드로 intensity 판정

3. record_microphone(timeout: int = 10) -> str
   - SpeechRecognition + PyAudio로 마이크 녹음
   - 임시 wav 파일 저장 후 경로 반환
   - 실패 시 빈 문자열 반환

그리고 tests/test_voice.py도 만들어줘:
- analyze_speech_intensity가 4가지 intensity를 올바르게 분류하는지
  (API 키 없는 환경에서도 키워드 폴백으로 동작해야 함)
- win_rate_bonus가 CLAUDE.md 수치 테이블과 일치하는지
- 반환 dict에 필수 키가 모두 있는지
- transcribe_speech가 에러 없이 폴백 동작하는지
  (실제 파일 없어도 빈 문자열 반환으로 처리)

테스트 실행:
  python -m pytest tests/test_voice.py -v

완료 후:
  CLAUDE.md S4 체크박스 완료 표시, 다음 세션 목표를 S5로 업데이트
  git add -A && git commit -m "[S4] voice_agent STT 음성 에이전트 구현"
```

---

## ⬜ S5 — agents/match_agent.py 검증

```
CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 S4 커밋이 있는지 확인해줘.
S4 커밋이 없으면 "S4 먼저 완료해주세요"라고 알려줘.

S5 작업이야. agents/match_agent.py를 열어서 확인해줘.
수정 대상: agents/match_agent.py만. 다른 파일은 읽기 전용.

확인 항목:
1. 4개 함수가 모두 있는지:
   - generate_match_narrative(gs, formation, opponent, half, score_home, score_away, result)
   - generate_halftime_speech(gs, speech_key, opponent, score_home, score_away)
   - generate_post_match_speech(gs, speech_key, opponent, result, score_home, score_away)
   - generate_press_conference(gs, choice_key, opponent, result, score_home, score_away)
2. OpenAI 클라이언트를 사용하는지 (Anthropic SDK면 교체 필요)
3. OPENAI_API_KEY 없을 때 예외 없이 폴백 텍스트를 반환하는지
4. 한국어 응답을 요청하는지
5. max_tokens가 300 이하로 제한되어 있는지 (비용 절감)

문제 없으면 "S5 검증 완료" 출력 후:
  git add -A && git commit -m "[S5] match_agent 검증 완료"
문제 있으면 해당 부분만 수정하고 커밋.
```

---

## ✅ S6 — agents/training_agent.py 검증 (완료, S2 선구현)

```
CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 커밋 이력 보여줘.

S6 검증 작업이야. agents/training_agent.py를 열어서 확인해줘:

1. generate_training_narrative(gs, training_key, effects, next_opponent) 함수가 있는지
2. OpenAI API 키 없을 때 예외 없이 폴백 텍스트를 반환하는지
3. 훈련 유형 3가지(회복/체력/전술)를 구분해서 다른 톤으로 프롬프트를 구성하는지
4. 한국어 응답을 요청하는지
5. OpenAI 클라이언트를 사용하는지 (Anthropic SDK면 교체 필요)

문제 없으면 "S6 검증 완료" 출력 후:
  git add -A && git commit -m "[S6] training_agent 검증 완료"
문제 있으면 해당 부분만 수정하고 커밋.
```

---

## ⬜ S7 — app.py 통합 연결

```
CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 S3, S4 커밋이 모두 있는지 확인해줘.
없는 세션이 있으면 해당 세션 먼저 완료해달라고 알려줘.

S7 작업이야. app.py를 수정해줘.
수정 대상: app.py만. 다른 파일은 읽기 전용.

작업 내용 2가지:

── 1. relegation_agent 연결 ──
- import 추가: from agents.relegation_agent import calculate_relegation_probability
- render_sidebar()의 강등 확률 표시 부분 교체:
  기존: simulator.py의 relegation_probability(gs) 단순 추정값
  변경: calculate_relegation_probability(gs)["probability"]
- 사이드바에 analysis 텍스트(2~3문장) 작게 표시
- is_mathematically_relegated == True이면 빨간 경고 배너 표시
- is_mathematically_safe == True이면 초록 안전 배너 표시
- check_ending() 앞에 relegation_agent 결과를 먼저 확인:
  is_mathematically_relegated == True이면 즉시 relegation 엔딩 처리

── 2. STT 하프타임 흐름 추가 ──
- import 추가:
  from agents.voice_agent import transcribe_speech, analyze_speech_intensity
- render_halftime() 함수에 두 가지 입력 경로 추가:
  경로 A — [🎙️ 음성으로 스피치하기]
    → st.file_uploader("오디오 파일 업로드", type=["mp3","wav","m4a"]) 표시
    → 파일 업로드되면 임시 저장 후 transcribe_speech() 호출
    → analyze_speech_intensity() 호출
    → 분석 결과(intensity 한국어 레이블, win_rate_bonus, summary) 표시
    → [이 스피치로 후반 시작] 버튼 → is_voice=True로 수치 반영
      (win_rate_bonus에 +0.02 추가 적용)
    → 후반전 simulate_second_half() 호출 시 speech_key="voice" 대신
      voice_bonus를 직접 넘기는 방식 사용
  경로 B — [📝 선택지로 스피치하기]  ← 기존 로직 그대로 유지

수정 완료 후:
  python -m pytest tests/ -v
  CLAUDE.md S7 체크박스 완료 표시, 다음 세션 목표를 S8로 업데이트
  git add -A && git commit -m "[S7] app.py relegation_agent + STT 하프타임 흐름 연결"
```

---

## ⬜ S8 — 통합 테스트 + 밸런스 검증

```
CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 S7까지 커밋이 있는지 확인해줘.

S8 작업이야. tests/ 폴더만 수정 가능. 다른 파일은 읽기 전용.

작업 순서:

1. 기존 테스트 전체 실행
   python -m pytest tests/ -v
   실패 테스트가 있으면 원인 분석해서 알려줘 (수정은 내가 지시할게)

2. tests/test_balance.py 신규 생성 — 밸런스 시뮬레이션
   아래 시나리오를 각 1000회 실행해서 결과 분포 출력:
   - 시나리오 A: 포메이션 4-3-3, 하프타임 motivate, 기자회견 careful, 매 경기 전 회복훈련
   - 시나리오 B: 포메이션 4-5-1, 하프타임 calm, 기자회견 humor, 훈련 없음
   - 시나리오 C: 포메이션 3-4-3, 하프타임 scold, 기자회견 aggressive, 매 경기 전 전술훈련
   각 시나리오: 평균 최종 승점, 생존율(%), 강등율(%), sacked율(%) 출력

3. 밸런스 통과 기준 (자동 판정해줘):
   - 시나리오 A(최선): survival율 > 50%
   - 시나리오 C(최악): relegation율 + sacked율 > 40%
   - 어떤 시나리오도 survival 100% 또는 relegation 100% 이면 안 됨
   기준 미달 항목이 있으면 어떤 수치를 얼마나 조정하면 좋을지 제안해줘
   (수정은 내가 지시할게, 이 세션에서 simulator.py 수정 금지)

4. 결과를 표로 출력해줘

완료 후:
  CLAUDE.md S8 체크박스 완료 표시, 알려진 이슈에 밸런스 결과 요약 추가
  git add -A && git commit -m "[S8] 통합 테스트 + 밸런스 검증"
```

---

## ⬜ S9 — README.md

```
CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 S8 커밋이 있는지 확인해줘.

S9 작업이야. README.md를 새로 만들어줘.
신규 생성 대상: README.md만. 다른 파일은 건드리지 마.

포함 내용 (순서대로, 한국어):

1. 게임 소개 — 한 문단
2. 스크린샷 자리 <!-- screenshot here --> 주석으로 표시
3. 설치 방법
   pip install openai streamlit speechrecognition pyaudio pytest
4. 실행 방법
   - OpenAI API 키 있을 때 (LLM 내러티브 + STT 활성)
   - API 키 없을 때 (수치 기반 모드, STT 비활성)
5. 게임 플로우 — 텍스트 다이어그램
   경기 전(포메이션 선택) → 전반 → 하프타임(음성/선택지 스피치) → 후반 → 경기 후 → 기자회견 → (반복) → 엔딩
6. STT 사용 방법 — 하프타임 음성 스피치 사용법 간략히
7. 파일 구조 — CLAUDE.md 파일 역할 지도 간략화
8. 엔딩 3가지 설명 (survival / relegation / sacked)
9. 세션별 개발 현황 표

완료 후:
  CLAUDE.md S9 체크박스 완료 표시
  git add -A && git commit -m "[S9] README.md 작성"
```

---

## 긴급 패치 — 버그 수정

```
CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 현재 커밋 상태 확인해줘.

버그 수정 작업이야. 아래 증상을 확인하고 수정해줘:

[증상을 여기에 구체적으로 적어줘]
예) "하프타임 스피치 후 morale이 100을 초과하는 경우 있음"
예) "remain_round가 0인데 ending 화면으로 안 넘어감"
예) "rival_teams 순회 시 KeyError 발생"

수정 규칙:
- CLAUDE.md 절대 규칙 위반 금지
- GameState 스키마 변경 금지
- 수정 파일과 변경 내용 명확히 알려줘
- 수정 후 관련 테스트 실행해서 결과 보여줘

완료 후:
  CLAUDE.md 알려진 이슈 업데이트
  git add -A && git commit -m "[hotfix] {버그 내용 한 줄}"
```

---

## 수치 밸런스 조정

```
CLAUDE.md를 읽고 시작해줘.

세션 시작 전 git log --oneline -5 실행해서 현재 커밋 상태 확인해줘.

수치 조정 작업이야. 아래 항목만 수정해줘:

[조정 내용을 여기에 적어줘]
예) "motivate 스피치 win_rate_bonus를 0.06 → 0.08로"
예) "패배 시 morale 감소를 -10 → -7로 완화"
예) "STT high_positive win_rate_bonus를 0.10 → 0.12로"

수정 가능 파일: simulator.py 또는 training.py 또는 agents/voice_agent.py 중 해당 파일만.
수정 후 CLAUDE.md 수치 밸런스 테이블도 동일하게 업데이트해줘.
테스트 실행: python -m pytest tests/ -v

완료 후:
  git add -A && git commit -m "[balance] {조정 내용 한 줄}"
```
