"""
app.py ga qo'shiladigan NLP endpointlari.

1) Faylning boshiga import qo'shing:
   from nlp_analyzer import run_nlp_analysis

2) Quyidagi endpointlarni app.py ga ko'chiring.
"""

# ─── NLP API ENDPOINTLARI ───────────────────────────────────────────

@app.route('/api/nlp/report', methods=['GET'])
def get_nlp_report():
    """Barcha NLP tahlillarini qaytaradi"""
    try:
        if df is None or len(df) == 0:
            return jsonify({'success': False, 'error': 'Ma\'lumot yuklanmagan'}), 400
        result = run_nlp_analysis(df)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/nlp/keywords', methods=['GET'])
def get_nlp_keywords():
    """Top kalit so'zlar"""
    try:
        if df is None or len(df) == 0:
            return jsonify({'keywords': []}), 200
        from nlp_analyzer import NLPLogAnalyzer
        analyzer = NLPLogAnalyzer(df)
        top_n = int(request.args.get('top_n', 30))
        keywords = analyzer.extract_keywords(top_n=top_n)
        return jsonify({'keywords': keywords, 'total': len(keywords)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/nlp/errors', methods=['GET'])
def get_nlp_errors():
    """Xatolik tasnifi"""
    try:
        if df is None or len(df) == 0:
            return jsonify({}), 200
        from nlp_analyzer import NLPLogAnalyzer
        analyzer = NLPLogAnalyzer(df)
        result = analyzer.classify_errors()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/nlp/templates', methods=['GET'])
def get_nlp_templates():
    """Log shablonlari"""
    try:
        if df is None or len(df) == 0:
            return jsonify({'templates': []}), 200
        from nlp_analyzer import NLPLogAnalyzer
        analyzer = NLPLogAnalyzer(df)
        top_n = int(request.args.get('top_n', 20))
        templates = analyzer.extract_templates(top_n=top_n)
        return jsonify({'templates': templates, 'total': len(templates)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/nlp/action-groups', methods=['GET'])
def get_nlp_action_groups():
    """Amallarning semantik guruhlari"""
    try:
        if df is None or len(df) == 0:
            return jsonify({}), 200
        from nlp_analyzer import NLPLogAnalyzer
        analyzer = NLPLogAnalyzer(df)
        groups = analyzer.group_actions_semantically()
        return jsonify(groups)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/nlp/ngrams', methods=['GET'])
def get_nlp_ngrams():
    """N-gramlar"""
    try:
        if df is None or len(df) == 0:
            return jsonify({'bigrams': [], 'trigrams': []}), 200
        from nlp_analyzer import NLPLogAnalyzer
        analyzer = NLPLogAnalyzer(df)
        n    = int(request.args.get('n', 2))
        top  = int(request.args.get('top_n', 20))
        grams = analyzer.extract_ngrams(n=n, top_n=top)
        return jsonify({'ngrams': grams, 'n': n})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
