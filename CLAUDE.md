# CLAUDE.md

You are working on **Blast Radius** (repository: Arka).

---

## 📚 Before Starting Any Task

### 1. Read Project Context

Read these files in order:

1. **ai-context/00_identity.md** - Project mission, vision, and philosophy
2. **ai-context/02_current_state.md** - What's completed and what's remaining
3. **ai-context/03_architecture.md** - System architecture and data flow
4. **ai-context/04_graph_model.md** - Graph data structures and relationships
5. **ai-context/05_tree_sitter.md** - Tree-sitter parsing configuration
6. **ai-context/06_backend.md** - Backend service details
7. **ai-context/07_frontend.md** - Frontend service details
8. **ai-context/08_api_contracts.md** - API specifications
9. **ai-context/09_coding_rules.md** - Coding standards and conventions
10. **ai-context/10_task_workflow.md** - Task execution workflow
11. **ai-context/11_prompt_patterns.md** - Prompt engineering patterns
12. **ai-context/12_testing.md** - Testing strategies
13. **ai-context/13_demo.md** - Demo preparation
14. **ai-context/14_roadmap.md** - Project roadmap and priorities
15. **ai-context/15_glossary.md** - Project terminology

### 2. Review Available Skills

Explore the **skills/** directory for domain-specific knowledge:

- **skills/analysis/** - Code analysis, graph analysis, impact analysis
- **skills/development/** - Frontend, backend, AI service development
- **skills/testing/** - Unit testing, integration testing
- **skills/deployment/** - Docker, cloud deployment

---

## 🎯 Core Principles

### 1. Static Analysis First

**Graphs decide. LLMs explain.**

- Always use static analysis (AST, graphs) as the source of truth
- LLMs should only explain graph-derived results
- Never make decisions based solely on LLM output
- Static analysis provides deterministic, verifiable results

### 2. Separation of Concerns

Keep responsibilities separate:

- **Frontend**: UI, user interaction, visualization
- **Backend**: API gateway, request routing, authentication
- **AI Service**: Core analysis, graph building, traversal

### 3. Do Not Rewrite Working Code

- Extend existing modules instead of rewriting
- Preserve existing functionality
- Add new features incrementally
- Maintain backward compatibility

### 4. One Feature Per Task

- Implement exactly one feature per task
- Keep changes focused and minimal
- Test each feature independently
- Document changes thoroughly

---

## 🛠️ Development Workflow

### 1. Search Existing Code

Before writing new code:

```bash
# Search for existing implementations
rg "function_name" ai-service/
rg "class_name" ai-service/
rg "pattern" .

# Check existing tests
grep -r "test_" tests/

# Review related modules
cat ai-service/analysis/repository_parser.py
```

### 2. Reuse Existing Modules

- Check if functionality already exists
- Extend existing classes instead of creating new ones
- Use existing utilities and helpers
- Follow existing patterns and conventions

### 3. Implement Incrementally

```python
# Good: Extend existing functionality
def new_feature(self):
    # Use existing methods
    result = self.existing_method()
    # Add new logic
    return self.process_result(result)

# Bad: Rewrite everything
def new_feature(self):
    # Don't reinvent the wheel
    pass
```

---

## 📝 After Implementation

### 1. Update Documentation

- Update relevant ai-context files
- Add examples and usage patterns
- Document new APIs and endpoints
- Update architecture diagrams

### 2. Update Roadmap

- Mark completed tasks in ai-context/14_roadmap.md
- Add new tasks as they're identified
- Update priorities based on dependencies
- Track progress against milestones

### 3. Explain Changes

For each changed file, provide:

- **Purpose**: Why this change was needed
- **Implementation**: What was changed and how
- **Impact**: How this affects other components
- **Testing**: How the change was tested

### 4. List Follow-up Improvements

- Identify future enhancements
- Note performance optimizations
- Suggest additional test cases
- Document known limitations

---

## 🎨 Code Quality Standards

### 1. Optimize For

✅ **Correctness** - Code must work as intended
✅ **Maintainability** - Code must be easy to understand and modify
✅ **Deterministic Analysis** - Static analysis must produce consistent results
✅ **Performance** - Code must be efficient
✅ **Readability** - Code must be clear and well-documented

### 2. Avoid

❌ **Cleverness** - Overly complex solutions
❌ **Premature Optimization** - Optimize only when needed
❌ **Magic Numbers** - Use named constants
❌ **Duplicate Code** - DRY principle
❌ **Unnecessary Abstraction** - Keep it simple

---

## 🧪 Testing Requirements

### 1. Test Coverage

- All new code must have tests
- Tests should cover happy paths and edge cases
- Use both unit tests and integration tests
- Aim for >80% test coverage

### 2. Test Types

- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test component interactions
- **API Tests**: Test HTTP endpoints
- **E2E Tests**: Test complete user flows

### 3. Test Quality

- Tests should be fast
- Tests should be deterministic
- Tests should be isolated
- Tests should be maintainable

---

## 🚀 Deployment Guidelines

### 1. Environment Configuration

- Use environment variables for configuration
- Provide sensible defaults
- Document required variables
- Use .env files for development

### 2. Docker Best Practices

- Use multi-stage builds
- Minimize image sizes
- Use appropriate base images
- Document build process

### 3. Service Communication

- Use service names for inter-service communication
- Handle connection errors gracefully
- Implement retry logic for transient failures
- Use health checks

---

## 📞 Communication

### 1. Commit Messages

Use conventional commits:

```
feat: Add new feature
fix: Fix bug
refactor: Refactor code
docs: Update documentation
test: Add tests
chore: Maintenance tasks
```

### 2. Pull Requests

- Provide clear description of changes
- Reference related issues
- Include screenshots for UI changes
- Document breaking changes
- Request specific reviews

### 3. Code Reviews

- Be constructive and specific
- Suggest improvements, not just point out problems
- Focus on code quality, not personal style
- Approve when acceptable, not when perfect

---

## 🎯 Hackathon Specific

### Focus Areas

1. **Complete MVP**: Finish all core features
2. **Polish UI**: Make the demo shine
3. **Prepare Demo**: Practice the 3-minute script
4. **Document Everything**: README, setup instructions, usage examples

### Success Criteria

- ✅ All core features implemented
- ✅ Demo script rehearsed
- ✅ Documentation complete
- ✅ Deployment ready
- ✅ Judges can understand and use the product

---

## 📚 Additional Resources

- [BLAST_RADIUS_README.md](BLAST_RADIUS_README.md) - Complete project documentation
- [README.md](README.md) - Original Arka project documentation
- [skills/](skills/) - Domain-specific skills and knowledge
- [ai-context/](ai-context/) - Project context and architecture

---

**Remember**: Every code change has a blast radius. See it before production does. 🚀