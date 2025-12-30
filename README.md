# Auto-Turntable (Raspberry Pi Music Automation)

> **"전원만 켜면, 나만의 덱(Deck)이 돌아갑니다. 끊긴 곳에서부터 다시 시작하는 감성 턴테이블."**

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-OS-C51A4A?style=flat&logo=raspberry-pi&logoColor=white)
![VLC](https://img.shields.io/badge/VLC-LibVLC-FF8800?style=flat&logo=vlc&logoColor=white)

---

## 1. 프로젝트 개요 (Overview)

### 목표
라즈베리파이를 활용하여 별도의 조작 없이 전원 인가만으로 작동하는 **자동 음악 재생 시스템**을 구축합니다.  
단순한 랜덤 재생이 아닌, 카드 덱(Deck) 방식의 셔플 로직과 상태 저장(State Persistence) 기능을 통해 **실제 턴테이블이나 카세트테이프처럼 듣던 곡 이후부터 자연스럽게 이어지는 사용자 경험(UX)**을 제공합니다.

### 핵심 기능
- **Auto-Shuffle Deck**: 전체 라이브러리를 하나의 덱으로 구성하여, 모든 곡을 다 들을 때까지 중복 없이 재생
- **Smart Resume**: 전원이 꺼져도 현재 덱의 상태와 재생 기록을 기억하여, 재부팅 시 끊긴 지점부터 즉시 연결
- **Headless Architecture**: 모니터나 키보드 없이(Headless) 스피커만 연결된 환경에서도 안정적 구동

---

## 2. 전체 아키텍처 (Architecture)

1. **Boot & Init**: 시스템 부팅 시 `main.py` 자동 실행
2. **Library Scan**: 지정된 경로(`music` 파일 참조) 내의 음원 파일 스캔 (`.mp3` 등)
3. **State Check**: 
   - 기존 `state.json` 확인
   - 저장된 덱(Deck)이 있다면 **복원(Resume)**
   - 없다면 새로운 **셔플 덱 생성(New Build)**
4. **Playback Loop**:
   - `Deck`에서 트랙 Pop → `VLC Player`로 재생
   - 재생 완료 시 `History` 기록 및 `State` 저장 (Atomic Save)
   - 덱 소진 시 자동 **Reshuffle**

---

## 3. 핵심 컴포넌트 상세 (System Components)

### 3.1 Playback Engine (VLC Integration)
- **역할**: 다양한 오디오 코덱의 안정적 재생 및 하드웨어 제어
- **기술 스택**: `libvlc` (C bindings) + `python-vlc`
- **핵심 구현**:
  - `play_track_blocking()`: 동기식 재생 처리를 통해 트랙 간 간섭 방지
  - **Headless Optimization**: 라즈베리파이 CLI 환경에서 GUI(X11) 오류를 방지하기 위해 `--no-xlib`, `--quiet` 인스턴스 옵션 적용

### 3.2 Recommendation Logic (The Shuffle Deck)
- **역할**: 중복 없는 랜덤 재생을 보장하는 알고리즘
- **구현 방식**:
  - 단순 `random.choice`가 아닌 **Fisher-Yates Shuffle** 개념의 덱 시스템 차용
  - `[Track A, Track B, ... Track Z]` 리스트를 생성 후 `pop(0)` 방식으로 소모
  - 덱이 비워지면(`len(deck) == 0`) 전체 트랙을 다시 섞어 새로운 덱 생성
- **장점**: 수천 곡의 라이브러리에서도 모든 곡을 한 번씩 다 듣기 전까지는 중복되지 않음

### 3.3 State Persistence (JSON Manager)
- **역할**: 전원 차단 등 돌발 상황에도 재생 연속성을 유지
- **구현 방식**:
  - Python `dataclasses`를 활용한 상태 객체(`PlayerState`) 정의
  - 트랙 재생이 끝날 때마다 `state.json`에 남은 덱과 히스토리를 직렬화하여 저장
  - **Fail-Safe**: 전원이 갑자기 뽑혀도, 마지막으로 완곡한 시점의 데이터가 보존됨

---

## 4. 설치 및 실행 (Getting Started)

### 환경 설정 (Environment)
이 프로젝트는 **Raspberry Pi OS (Bullseye)** 및 **Python 3.9** 환경에 최적화되어 있습니다.

### 설치 단계 (Installation)
1. **시스템 패키지 설치 (필수)**
   VLC 플레이어의 코어 라이브러리가 필요합니다.
   ```bash
   sudo apt-get update
   sudo apt-get install vlc libvlc-dev
2. **프로젝트 클론 및 패키지 설치**
```bash
   git clone https://github.com/YOUR_USERNAME/auto-turntable.git
   cd auto-turntable
   pip install -r requirements.txt
```

3. **음악 폴더 경로 설정**
   프로젝트 루트에 `music` 파일(확장자 없음)을 생성하고, 음악 폴더 경로를 입력합니다.
```bash
   echo "/home/pi/Music" > music
```

4. **테스트 실행**
```bash
   python main.py
```

### 부팅 시 자동 실행 (systemd)

라즈베리파이 전원만 켜면 자동으로 음악이 재생되도록 서비스를 등록합니다.

1. **서비스 파일 생성**
```bash
   sudo nano /etc/systemd/system/turntable.service
```

2. **아래 내용 입력** (경로는 본인 환경에 맞게 수정)
```ini
   [Unit]
   Description=Auto Turntable Music Player
   After=sound.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/auto-turntable
   ExecStart=/usr/bin/python3 /home/pi/auto-turntable/main.py
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
```

3. **서비스 등록 및 시작**
```bash
   sudo systemctl daemon-reload
   sudo systemctl enable turntable.service
   sudo systemctl start turntable.service
```

4. **상태 확인**
```bash
   sudo systemctl status turntable.service
```

---

## 5. 사용법 (Usage)

| 동작 | 설명 |
|------|------|
| 전원 ON | 자동으로 음악 재생 시작 |
| 전원 OFF | 현재 상태 저장 (다음 부팅 시 이어서 재생) |
| 덱 초기화 | `state.json` 삭제 또는 코드에서 `reset_state()` 호출 |

---

## 6. 파일 구조 (Project Structure)
```
auto-turntable/
├── main.py          # 메인 실행 파일
├── library.py       # 음악 파일 스캔
├── player_vlc.py    # VLC 재생 엔진
├── recommender.py   # 셔플 덱 생성
├── state.py         # 상태 저장/복원
├── requirements.txt # Python 의존성
├── music            # 음악 폴더 경로 (사용자 생성)
└── state.json       # 재생 상태 (자동 생성)