# skill-index

Community-curated convention skills for [skillgen](https://github.com/mmoselhy/skillgen).

## What is this?

This repository hosts reusable skill files that `skillgen --enrich` can discover and install. Each skill contains language- and framework-specific conventions that AI agents (Claude Code, Cursor, etc.) use to write code matching your project's patterns.

## Structure

```
skills/
├── python/         # Python skills (pytest, FastAPI, Django, Flask, SQLAlchemy, structlog)
├── typescript/     # TypeScript skills (Next.js, React, Vitest)
├── javascript/     # JavaScript skills (Express)
├── go/             # Go skills (Gin, Cobra, stdlib)
├── rust/           # Rust skills (Actix, Tokio)
└── java/           # Java skills (Spring Boot)
```

## Usage

```bash
# Search for matching skills
skillgen ./my-project --enrich

# Install matched skills
skillgen ./my-project --enrich --apply

# Cherry-pick specific skills
skillgen ./my-project --enrich --apply --pick 1,3
```

## Contributing

To add a community skill:

1. Create a `.md` file in the appropriate `skills/<language>/` directory
2. Add an entry to `index.json` with the required fields
3. Submit a pull request

### Skill file format

```markdown
# Skill Name

## Section
- **Pattern name**: Description with `code_examples`
```

### Index entry format

```json
{
  "id": "unique-slug",
  "name": "Human Readable Name",
  "language": "python",
  "framework": null,
  "categories": ["testing", "error-handling"],
  "path": "skills/python/my-skill.md",
  "description": "One-line description of what this skill covers."
}
```

## License

MIT
