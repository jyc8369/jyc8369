# GitHub Showcase 자동 가져오기 규격

이 저장소의 `showcase.json`은 GitHub 저장소 쇼케이스 사이트가 프로젝트 목록을 자동으로 구성할 때 사용하는 설정 파일입니다.

## 파일 위치

```text
jyc8369/jyc8369/showcase.json
```

## 처리 흐름

1. GitHub API에서 `jyc8369`의 공개 저장소 목록을 가져옵니다.
2. `archived: true`인 저장소와 `source.exclude`에 지정된 저장소를 제외합니다.
3. 공개·비보관 저장소는 모두 `projects` 대상에 포함합니다.
4. `showcase.json`의 대표 프로젝트 여부와 노출 순서를 적용합니다.
5. GitHub 기본 정보와 설정 파일의 사용자 지정 정보를 합칩니다.
6. API 요청이 실패하면 마지막 정상 데이터 또는 설정 파일의 기본 데이터를 사용합니다.

## 현재 적용 대상

현재 공개 상태이며 보관되지 않은 저장소 전체를 반영합니다.

- `Minecraft_Mod_Translator_Gemini`
- `realesrgan_gui_korean`
- `Icon_Bundler`
- `Codex_Multi_Login`
- `Chatgpt_Account_Generator`

다음 저장소는 대상에서 제외합니다.

- `jyc8369`: 프로필 설정 저장소
- `Subculture_Tracker`: 보관된 저장소
- 비공개 저장소: 외부 공개 API 대상에서 제외

## 데이터 구조

```json
{
  "version": 1,
  "source": {
    "githubUser": "jyc8369",
    "exclude": ["jyc8369"],
    "includeArchived": false
  },
  "projects": [
    {
      "repo": "Repository_Name",
      "featured": true,
      "order": 1,
      "category": "AI Tool",
      "summary": "",
      "tags": [],
      "demoUrl": "",
      "coverImage": ""
    }
  ]
}
```

## 필드 규칙

| 필드 | 설명 |
| --- | --- |
| `version` | 설정 파일 규격 버전 |
| `source.githubUser` | GitHub 사용자명 |
| `source.exclude` | 자동 가져오기에서 제외할 저장소명 |
| `source.includeArchived` | 보관된 저장소 포함 여부. 기본값은 `false` |
| `projects[].repo` | GitHub 저장소명 |
| `projects[].featured` | 대표 프로젝트 노출 여부 |
| `projects[].order` | 프로젝트 노출 순서 |
| `projects[].category` | 쇼케이스 카테고리 |
| `projects[].summary` | GitHub 설명을 덮어쓸 사용자 지정 설명 |
| `projects[].tags` | 화면에 표시할 태그 |
| `projects[].demoUrl` | 배포 데모 주소 |
| `projects[].coverImage` | 프로젝트 대표 이미지 주소 |

## 운영 규칙

- 저장소명은 GitHub의 실제 저장소명과 정확히 일치해야 합니다.
- 공개·비보관 저장소는 모두 설정 파일의 프로젝트 대상에 포함합니다.
- 대표 프로젝트는 `featured: true`와 `order`를 함께 지정합니다.
- 저장소 기본 설명을 사용할 경우 `summary`를 빈 문자열로 둡니다.
- 공개 저장소가 새로 추가되면 API 기본 정보로 자동 목록에 포함됩니다.
- 보관 저장소는 별도 Archive 영역에 노출하지 않습니다.
- JSON 문법을 유지해야 하며, 변경 후 파싱 오류가 없어야 합니다.
