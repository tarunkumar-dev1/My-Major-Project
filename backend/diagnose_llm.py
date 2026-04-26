"""
Comprehensive LLM Integration Diagnostic Script
Tests every layer: env config, Gemini SDK, embeddings, text generation, and full pipeline.
"""
import sys
import os
import json
import traceback

# Ensure we can import from the project
sys.path.insert(0, os.path.dirname(__file__))

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"
INFO = "[INFO]"

results = []

def test(name, func):
    """Run a test and record the result."""
    print(f"\n{'='*60}")
    print(f" TEST: {name}")
    print(f"{'='*60}")
    try:
        func()
        results.append((name, True, None))
    except Exception as e:
        results.append((name, False, str(e)))
        traceback.print_exc()

# ──────────────────────────────────────────────────────────────
# 1. Environment & Config
# ──────────────────────────────────────────────────────────────
def test_env_config():
    from config import Config
    key = Config.GEMINI_API_KEY
    if not key:
        print(f"{FAIL} GEMINI_API_KEY is empty/not set.")
        print(f"{INFO} Create a '.env' file in backend/ with:")
        print(f"       GEMINI_API_KEY=your-google-api-key-here")
        raise ValueError("GEMINI_API_KEY not configured")
    masked = key[:6] + "..." + key[-4:]
    print(f"{PASS} GEMINI_API_KEY is set: {masked}")
    print(f"{INFO} AI_MODEL_NAME = {Config.AI_MODEL_NAME}")

# ──────────────────────────────────────────────────────────────
# 2. Gemini SDK Import & Configuration
# ──────────────────────────────────────────────────────────────
def test_gemini_sdk():
    import google.generativeai as genai
    from config import Config
    genai.configure(api_key=Config.GEMINI_API_KEY)
    print(f"{PASS} google.generativeai imported and configured successfully.")
    
    # List available models
    models = [m.name for m in genai.list_models() if "embed" in m.name.lower() or "gemini" in m.name.lower()]
    print(f"{INFO} Available models (sample): {models[:8]}")

# ──────────────────────────────────────────────────────────────
# 3. Embedding API
# ──────────────────────────────────────────────────────────────
def test_embeddings():
    import google.generativeai as genai
    from config import Config
    genai.configure(api_key=Config.GEMINI_API_KEY)

    test_skills = ["Python", "Machine Learning", "Docker"]
    print(f"{INFO} Requesting embeddings for: {test_skills}")
    
    response = genai.embed_content(
        model=Config.AI_MODEL_NAME,
        content=test_skills,
        task_type="SEMANTIC_SIMILARITY"
    )
    
    embeddings = response['embedding']
    print(f"{PASS} Received {len(embeddings)} embedding vectors.")
    print(f"{INFO} Vector dimension: {len(embeddings[0])}")
    print(f"{INFO} First 5 values of 'Python' embedding: {embeddings[0][:5]}")

# ──────────────────────────────────────────────────────────────
# 4. Text Generation (LLM) API
# ──────────────────────────────────────────────────────────────
def test_text_generation():
    import google.generativeai as genai
    from config import Config
    genai.configure(api_key=Config.GEMINI_API_KEY)

    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    prompt = "Respond with exactly: {\"status\": \"ok\"}"
    print(f"{INFO} Sending test prompt to gemini-2.0-flash-lite...")
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    print(f"{PASS} Received response: {text[:200]}")

# ──────────────────────────────────────────────────────────────
# 5. SimilarityEngine (project code)
# ──────────────────────────────────────────────────────────────
def test_similarity_engine():
    from app.ai_module.similarity import SimilarityEngine
    
    engine = SimilarityEngine.get_instance()
    print(f"{INFO} ai_enabled = {engine.ai_enabled}")
    
    if not engine.ai_enabled:
        raise RuntimeError("SimilarityEngine has ai_enabled=False (API key missing)")
    
    user_skills = ["Python", "Java", "HTML"]
    required_skills = ["Machine Learning", "Backend Development", "Web Development", "Data Analysis"]
    
    print(f"{INFO} User skills:     {user_skills}")
    print(f"{INFO} Required skills: {required_skills}")
    
    matches = engine.calculate_similarity_matrix(user_skills, required_skills)
    
    if not matches:
        raise RuntimeError("calculate_similarity_matrix returned empty results")
    
    print(f"{PASS} Got {len(matches)} similarity matches:")
    for m in matches:
        score_bar = "#" * int(m['similarity_score'] * 20)
        print(f"   {m['required_skill']:25s} <-> {m['best_user_match']:10s}  score={m['similarity_score']:.4f}  {score_bar}")

# ──────────────────────────────────────────────────────────────
# 6. Skill Gap Analysis (bridge_skill_gap)
# ──────────────────────────────────────────────────────────────
def test_skill_gap():
    from app.ai_module.similarity import SimilarityEngine
    
    engine = SimilarityEngine.get_instance()
    
    user_skills = ["Python", "SQL"]
    required_skills = ["Python", "TensorFlow", "PyTorch", "SQL", "MLOps", "Data Structures"]
    
    print(f"{INFO} User: {user_skills}")
    print(f"{INFO} Required: {required_skills}")
    
    result = engine.bridge_skill_gap(user_skills, required_skills, threshold=0.75)
    
    print(f"{PASS} Readiness Score:  {result['readiness_score']}%")
    print(f"{INFO} Covered skills:   {result['covered_skills']}")
    print(f"{INFO} Missing skills:   {result['missing_skills']}")
    print(f"{INFO} AI-matched:       {result['ai_matches']}")
    
    if result['readiness_score'] < 0 or result['readiness_score'] > 100:
        raise ValueError(f"Invalid readiness score: {result['readiness_score']}")

# ──────────────────────────────────────────────────────────────
# 7. Roadmap Generation (LLM-powered)
# ──────────────────────────────────────────────────────────────
def test_roadmap_generation():
    # We need the app context for database access
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.services.roadmap_service import RoadmapService
        service = RoadmapService()
        
        print(f"{INFO} ai_enabled = {service.ai_enabled}")
        if not service.ai_enabled:
            raise RuntimeError("RoadmapService has ai_enabled=False")
        
        missing = ["TensorFlow", "MLOps"]
        user = ["Python", "SQL"]
        career = "Machine Learning Engineer"
        
        print(f"{INFO} Generating roadmap for missing skills: {missing}")
        steps = service.generate_roadmap_steps(missing, user, career)
        
        if not steps:
            raise RuntimeError("No roadmap steps were generated")
        
        print(f"{PASS} Generated {len(steps)} roadmap steps:")
        for step in steps:
            modules = step.get('modules', [])
            print(f"   Step {step.get('step_number')}: {step.get('target_skill')} — {step.get('module_title')}")
            for mod in modules:
                print(f"      [{mod.get('level', '')}] {mod.get('title', '')}")

# ──────────────────────────────────────────────────────────────
# 8. Full End-to-End Pipeline (API simulation)
# ──────────────────────────────────────────────────────────────
def test_full_pipeline():
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.services.analysis_service import AnalysisService
        from app.database.connection import get_db
        
        db = get_db()
        user = db.users.find_one({"email": "ultimate@example.com"})
        if not user:
            raise RuntimeError("Test user not found in database")
        
        user_id = str(user['_id'])
        print(f"{INFO} Test user ID: {user_id}")
        
        service = AnalysisService()
        response, status_code = service.analyze_student_skills(
            user_id=user_id,
            submitted_skills=["Python", "SQL", "Git"],
            career_goal="Machine Learning Engineer"
        )
        
        if status_code != 200:
            raise RuntimeError(f"Analysis returned status {status_code}: {response}")
        
        print(f"{PASS} Full pipeline completed successfully!")
        print(f"{INFO} Readiness Score: {response.get('readiness_score')}%")
        print(f"{INFO} Covered:  {response.get('covered_skills')}")
        print(f"{INFO} Missing:  {response.get('missing_skills')}")
        print(f"{INFO} AI Matches: {response.get('ai_detected_matches')}")
        roadmap = response.get('roadmap', [])
        print(f"{INFO} Roadmap Steps: {len(roadmap)}")
        for step in (roadmap[:3] if roadmap else []):
            print(f"   -> {step.get('target_skill')}: {step.get('module_title')} ({len(step.get('modules',[]))} modules)")


# ──────────────────────────────────────────────────────────────
# RUN ALL TESTS
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + " LLM INTEGRATION DIAGNOSTIC ".center(60, "="))
    print("=" * 60)
    
    test("1. Environment & Config", test_env_config)
    test("2. Gemini SDK Import", test_gemini_sdk)
    test("3. Embedding API", test_embeddings)
    test("4. Text Generation API", test_text_generation)
    test("5. SimilarityEngine", test_similarity_engine)
    test("6. Skill Gap Analysis", test_skill_gap)
    test("7. Roadmap Generation (LLM)", test_roadmap_generation)
    test("8. Full End-to-End Pipeline", test_full_pipeline)
    
    # Summary
    print(f"\n\n{'='*60}")
    print(" DIAGNOSTIC SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    
    for name, ok, err in results:
        status = PASS if ok else FAIL
        suffix = f" — {err}" if err else ""
        print(f"  {status} {name}{suffix}")
    
    print(f"\n  Total: {passed} passed, {failed} failed out of {len(results)}")
    
    if failed > 0:
        print(f"\n  ** Some tests failed. Check the output above for details.")
        sys.exit(1)
    else:
        print(f"\n  ** All LLM integrations are working correctly!")
        sys.exit(0)
