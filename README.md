﻿# note-supporter

- `/` | 홈페이지(앱 소개, 설명)|
- User_app
  - `/login` | 로그인 |
  - `/logout` | 로그아웃 |
  - `/user` | 유저 정보 |
  - `/user/scripts` | 유저가 가진 스크립트 |
- Script_app
  - `/upload` | 오디오 업로드 페이지 |
    - s3에 저장 후 원본 스크립트 생성. 이후 `/make_script` 이동
  - `/choose_script` | 수정할 스크립트 선택 |
  - `/make_script` | 스크립트 수정 생성 |
    - 선택한 스크립트 제공하며 수정 옵션 제공
