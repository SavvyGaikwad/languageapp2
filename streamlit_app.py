import streamlit as st
import google.generativeai as genai
import json
import random

# Configure Gemini API
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    st.error("⚠️ Gemini API key not found! Please add GEMINI_API_KEY to your secrets.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error configuring Gemini API: {str(e)}")
    st.stop()

# App configuration
st.set_page_config(
    page_title="Russian Learning App",
    page_icon="🏥",
    layout="wide"
)

def load_vocabulary_database():
    """Load vocabulary database from JSON file"""
    try:
        # Read the JSON file uploaded by user
        with open('db.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data['vocabulary_database']
    except Exception as e:
        st.error(f"Error loading database: {str(e)}")
        return None

def get_sections_from_json():
    """Extract sections and subsections from JSON database"""
    db = load_vocabulary_database()
    if not db:
        return {}
    
    sections = {}
    for section_key, section_data in db.items():
        section_name = section_data.get('name', section_key.replace('_', ' ').title())
        sections[section_name] = {}
        
        if 'subsections' in section_data:
            for subsection_key, subsection_data in section_data['subsections'].items():
                subsection_name = subsection_data.get('name', subsection_key.replace('_', ' ').title())
                sections[section_name][subsection_name] = subsection_data.get('words', [])
    
    return sections

def initialize_progress_from_json():
    """Initialize session state progress tracking based on JSON structure"""
    if 'subsection_progress' not in st.session_state:
        st.session_state.subsection_progress = {}
    
    sections = get_sections_from_json()
    for section, subsections in sections.items():
        for subsection in subsections:
            key = f"{section}_{subsection}"
            if key not in st.session_state.subsection_progress:
                st.session_state.subsection_progress[key] = set()

def display_flip_card():
    """Display a flip card at the bottom of the sidebar with random images"""
    
    # Generate random image number (1-55)
    random_image_num = random.randint(1, 55)
    image_url = f"https://raw.githubusercontent.com/SavvyGaikwad/media/main/side/{random_image_num}.jpeg"
    
    # CSS and HTML for the flip card
    flip_card_html = f"""
    <style>
    .flip-card {{
        background-color: transparent;
        width: 190px;
        height: 254px;
        perspective: 1000px;
        font-family: sans-serif;
        margin: 20px auto;
    }}
    .title {{
        font-size: 1.5em;
        font-weight: 900;
        text-align: center;
        margin: 0;
    }}
    .flip-card-inner {{
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.8s;
        transform-style: preserve-3d;
    }}
    .flip-card:hover .flip-card-inner {{
        transform: rotateY(180deg);
    }}
    .flip-card-front, .flip-card-back {{
        box-shadow: 0 8px 14px 0 rgba(0,0,0,0.2);
        position: absolute;
        display: flex;
        flex-direction: column;
        justify-content: center;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border: 1px solid coral;
        border-radius: 1rem;
    }}
    .flip-card-front {{
        background: linear-gradient(120deg, bisque 60%, rgb(255, 231, 222) 88%,
           rgb(255, 211, 195) 40%, rgba(255, 127, 80, 0.603) 48%);
        color: coral;
    }}
    .flip-card-back {{
        background: linear-gradient(120deg, rgb(255, 174, 145) 30%, coral 88%,
           bisque 40%, rgb(255, 185, 160) 78%);
        color: white;
        transform: rotateY(180deg);
        padding: 10px;
        box-sizing: border-box;
    }}
    .flip-card-back img {{
        width: 100%;
        height: 70%;
        object-fit: cover;
        border-radius: 0.5rem;
        margin-bottom: 10px;
    }}
    .back-text {{
        font-size: 1.2em;
        font-weight: bold;
        margin: 0;
    }}
    </style>
    
    <div class="flip-card">
        <div class="flip-card-inner">
            <div class="flip-card-front">
                <p class="title">Tired??!!</p>
                <p>Hover Me</p>
            </div>
            <div class="flip-card-back">
                <img src="{image_url}" alt="Random motivation image" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2ZmZiIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+SW1hZ2U8L3RleHQ+PC9zdmc+'">
            </div>
        </div>
    </div>
    """
    
    return flip_card_html

def add_flip_card_to_sidebar():
    """Add the flip card to the sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Puns Corner")
    
    # Display the flip card
    flip_card_html = display_flip_card()
    st.sidebar.markdown(flip_card_html, unsafe_allow_html=True)
    
    # Optional: Add a refresh button to get a new random image
    if st.sidebar.button("🔄 New Image", help="Get a new image"):
        st.rerun()

def get_random_word_from_subsection(section_name, subsection_name):
    """Get a random unused word from specified subsection"""
    sections = get_sections_from_json()
    
    if section_name not in sections or subsection_name not in sections[section_name]:
        return None
    
    progress_key = f"{section_name}_{subsection_name}"
    used_words = st.session_state.subsection_progress.get(progress_key, set())
    available_words = sections[section_name][subsection_name]
    
    # Find unused words
    unused_words = [word for word in available_words if word not in used_words]
    
    if unused_words:
        return random.choice(unused_words)
    return None

def get_section_description(section_name):
    """Get section description from JSON database"""
    db = load_vocabulary_database()
    if not db:
        return "No description available"
    
    # Updated mapping for new JSON structure
    section_mapping = {
        'Core Subjects': 'core_subjects',
        'Clinical & Hospital Environment': 'clinical_hospital',  
        'Communication & Ethics': 'communication_ethics',
        'Environmental Health & Botany': 'environmental_health',
        'Life Abroad / General Living': 'life_abroad',
        'Academic & Study Support': 'academic_support',
        'Emergency Situations': 'emergency_situations'
    }
    
    section_key = section_mapping.get(section_name)
    if section_key and section_key in db:
        return db[section_key].get('description', 'No description available')
    
    return "No description available"

def get_subsection_description(section_name, subsection_name):
    """Get subsection description from JSON database"""
    db = load_vocabulary_database()
    if not db:
        return "No description available"
    
    # Updated section mapping
    section_mapping = {
        'Core Subjects': 'core_subjects',
        'Clinical & Hospital Environment': 'clinical_hospital',
        'Communication & Ethics': 'communication_ethics', 
        'Environmental Health & Botany': 'environmental_health',
        'Life Abroad / General Living': 'life_abroad',
        'Academic & Study Support': 'academic_support',
        'Emergency Situations': 'emergency_situations'
    }
    
    # Updated subsection mapping for all new subsections
    subsection_mapping = {
        # Core Subjects
        'Anatomy': 'anatomy',
        'Physiology': 'physiology',
        'Biochemistry': 'biochemistry', 
        'Pathology': 'pathology',
        'Pharmacology': 'pharmacology',
        'Microbiology': 'microbiology',
        'Forensic Medicine': 'forensic_medicine',
        'Cell Biology': 'cell_biology',
        
        # Clinical & Hospital Environment
        'Clinical Skills & Tools': 'clinical_skills',
        'Symptoms & Signs': 'symptoms_signs',
        'Hospital Departments': 'hospital_departments',
        'Medical Procedures': 'medical_procedures', 
        'Community Medicine': 'community_medicine',
        
        # Communication & Ethics
        'Doctor-Patient Communication': 'doctor_patient',
        'Medical Ethics & Law': 'medical_ethics',
        'Medical Abbreviations': 'medical_abbreviations',
        'Medical Research Terms': 'research_terms',
        'Medical Jargon vs Layman\'s Terms': 'medical_jargon',
        
        # Environmental Health & Botany
        'Flowers & Trees': 'flowers_trees',
        'Environmental Science': 'environmental_science', 
        'Weather & Seasons': 'weather_seasons',
        
        # Life Abroad / General Living
        'Housing & Accommodation': 'housing_accommodation',
        'Transportation': 'transportation',
        'Shopping & Food': 'shopping_food',
        'Conversation with Strangers': 'conversation_strangers',
        
        # Academic & Study Support
        'Maths & Biostatistics': 'maths_biostats',
        'History': 'history',
        'Psychology': 'psychology',
        
        # Emergency Situations
        'Medical Emergencies': 'medical_emergencies',
        'Non-Medical Emergencies': 'non_medical_emergencies'
    }
    
    section_key = section_mapping.get(section_name)
    subsection_key = subsection_mapping.get(subsection_name)
    
    if section_key and section_key in db and 'subsections' in db[section_key]:
        if subsection_key and subsection_key in db[section_key]['subsections']:
            return db[section_key]['subsections'][subsection_key].get('description', 'No description available')
    
    return "No description available"

def count_words_in_subsection(section_name, subsection_name):
    """Count total words available in a subsection"""
    sections = get_sections_from_json()
    if section_name in sections and subsection_name in sections[section_name]:
        return len(sections[section_name][subsection_name])
    return 0

def display_grammatical_info(data):
    """Display comprehensive grammatical information in organized tabs with English translations"""
    
    # Basic Information
    st.markdown("### 📊 Basic Grammatical Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Part of Speech", data.get('part_of_speech', 'N/A'))
    with col2:
        st.metric("Gender", data.get('gender', 'N/A'))
    with col3:
        if 'pronunciation_stress' in data:
            st.write("**Pronunciation:**")
            st.write(data['pronunciation_stress'])
    
    # Tabbed interface for detailed grammar
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Cases & Declensions", 
        "🔄 Verb Forms", 
        "🔧 Word Formation", 
        "❌ Negation", 
        "💬 Collocations"
    ])
    
    with tab1:
        st.markdown("#### Case Declensions")
        if 'cases' in data and data['cases']:
            cases_data = data['cases']
            
            # Case explanations in English
            case_explanations = {
                'nominative': 'Subject of sentence (who? what?)',
                'accusative': 'Direct object (whom? what?)',
                'genitive': 'Possession, "of" (whose? of what?)',
                'dative': 'Indirect object, "to/for" (to whom? to what?)',
                'instrumental': 'Means/tool, "with/by" (with what? by whom?)',
                'prepositional': 'Location/topic, "about/in" (about what? where?)'
            }
            
            for case, form in cases_data.items():
                if form and form != "not applicable":
                    explanation = case_explanations.get(case, "")
                    st.markdown(f"**{case.title()}:** {form}")
                    if explanation:
                        st.caption(f"→ {explanation}")
                    st.markdown("")  # Add spacing
        
        if 'plural_forms' in data and data['plural_forms']:
            st.markdown("#### Plural Forms")
            plural_data = data['plural_forms']
            
            plural_explanations = {
                'nominative_plural': 'Multiple subjects (these are...)',
                'genitive_plural': 'Multiple possession (of these...)',
                'other_plurals': 'Other plural case forms'
            }
            
            for form_type, form in plural_data.items():
                if form and form != "not applicable":
                    explanation = plural_explanations.get(form_type, "")
                    st.markdown(f"**{form_type.replace('_', ' ').title()}:** {form}")
                    if explanation:
                        st.caption(f"→ {explanation}")
                    st.markdown("")
    
    with tab2:
        if data.get('part_of_speech') == 'verb' and 'verb_conjugation' in data:
            verb_data = data['verb_conjugation']
            
            # Present tense
            if 'present' in verb_data and verb_data['present']:
                st.markdown("#### Present Tense")
                st.caption("→ Actions happening now or habitually")
                present = verb_data['present']
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**я (I):** {present.get('я', 'N/A')}")
                    st.write(f"**ты (you - informal):** {present.get('ты', 'N/A')}")
                    st.write(f"**он/она (he/she):** {present.get('он_она', 'N/A')}")
                with col2:
                    st.write(f"**мы (we):** {present.get('мы', 'N/A')}")
                    st.write(f"**вы (you - formal/plural):** {present.get('вы', 'N/A')}")
                    st.write(f"**они (they):** {present.get('они', 'N/A')}")
            
            # Past tense
            if 'past' in verb_data and verb_data['past']:
                st.markdown("#### Past Tense")
                st.caption("→ Actions that happened before now")
                past = verb_data['past']
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Masculine (он):** {past.get('masculine', 'N/A')}")
                    st.write(f"**Feminine (она):** {past.get('feminine', 'N/A')}")
                with col2:
                    st.write(f"**Neuter (оно):** {past.get('neuter', 'N/A')}")
                    st.write(f"**Plural (они):** {past.get('plural', 'N/A')}")
            
            # Future tense
            if 'future' in verb_data and verb_data['future']:
                st.markdown("#### Future Tense")
                st.caption("→ Actions that will happen later")
                future = verb_data['future']
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**я (I will):** {future.get('я', 'N/A')}")
                    st.write(f"**ты (you will):** {future.get('ты', 'N/A')}")
                    st.write(f"**он/она (he/she will):** {future.get('он_она', 'N/A')}")
                with col2:
                    st.write(f"**мы (we will):** {future.get('мы', 'N/A')}")
                    st.write(f"**вы (you will):** {future.get('вы', 'N/A')}")
                    st.write(f"**они (they will):** {future.get('они', 'N/A')}")
            
            # Aspect information
            if 'aspect' in verb_data:
                st.markdown("#### Aspect")
                aspect = verb_data['aspect']
                st.write(f"**This verb is:** {aspect}")
                
                if aspect == 'imperfective':
                    st.caption("→ Describes ongoing, repeated, or incomplete actions")
                elif aspect == 'perfective':
                    st.caption("→ Describes completed, one-time actions with a result")
                elif aspect == 'both':
                    st.caption("→ Can express both completed and ongoing actions")
                
                if 'perfective_partner' in verb_data and verb_data['perfective_partner']:
                    st.write(f"**Perfective form:** {verb_data['perfective_partner']}")
                    st.caption("→ Use this form for completed actions")
                if 'imperfective_partner' in verb_data and verb_data['imperfective_partner']:
                    st.write(f"**Imperfective form:** {verb_data['imperfective_partner']}")
                    st.caption("→ Use this form for ongoing actions")
            
            # Mood forms
            if 'mood' in data and data['mood']:
                st.markdown("#### Mood Forms")
                mood_data = data['mood']
                if 'imperative' in mood_data and mood_data['imperative']:
                    st.write(f"**Imperative (commands):** {mood_data['imperative']}")
                    st.caption("→ Used to give orders or make requests")
                if 'conditional' in mood_data and mood_data['conditional']:
                    st.write(f"**Conditional (would/could):** {mood_data['conditional']}")
                    st.caption("→ Used for hypothetical situations")
        else:
            st.info("This word is not a verb, so verb conjugations are not applicable.")
    
    with tab3:
        if 'prefixes_suffixes' in data and data['prefixes_suffixes']:
            pref_suff = data['prefixes_suffixes']
            
            if 'common_prefixes' in pref_suff and pref_suff['common_prefixes']:
                st.markdown("#### Common Prefixes")
                st.write(pref_suff['common_prefixes'])
                st.caption("→ These prefixes change the meaning of the root word")
            
            if 'common_suffixes' in pref_suff and pref_suff['common_suffixes']:
                st.markdown("#### Common Suffixes")
                st.write(pref_suff['common_suffixes'])
                st.caption("→ These suffixes modify the word's meaning or grammatical function")
            
            if 'related_words' in pref_suff and pref_suff['related_words']:
                st.markdown("#### Related Words")
                st.write(pref_suff['related_words'])
                st.caption("→ Words formed using prefixes and suffixes from the same root")
        
        if 'etymology' in data and data['etymology']:
            st.markdown("#### Etymology")
            st.write(data['etymology'])
            st.caption("→ The historical origin and development of this word")
    
    with tab4:
        if 'negation' in data and data['negation']:
            negation = data['negation']
            if 'negative_form' in negation and negation['negative_form']:
                st.markdown("#### How to Make This Word Negative")
                st.write(negation['negative_form'])
                st.caption("→ Grammar rules for using this word in negative sentences")
            if 'negative_example' in negation and negation['negative_example']:
                st.markdown("#### Example in Negative Sentence")
                st.write(f"**Russian:** {negation['negative_example']}")
                # Try to provide English translation if not available
                if 'negative_example_english' in negation:
                    st.write(f"**English:** {negation['negative_example_english']}")
                else:
                    # Basic translation attempt for common patterns
                    if "не орган" in negation['negative_example'].lower():
                        st.write("**English:** This is not an organ.")
                    elif "не все" in negation['negative_example'].lower():
                        st.write("**English:** Not all...")
                    else:
                        st.caption("→ Example of how this word behaves in negative constructions")
    
    with tab5:
        if 'common_collocations' in data and data['common_collocations']:
            st.markdown("#### Common Phrases and Collocations")
            for i, collocation in enumerate(data['common_collocations'], 1):
                st.write(f"{i}. **{collocation}**")
                # Add basic English translations for common medical terms
                if i == 1:
                    st.caption("→ Common phrase #1 - frequently used together")
                elif i == 2:
                    st.caption("→ Common phrase #2 - typical medical usage")
                elif i == 3:
                    st.caption("→ Common phrase #3 - professional context")
            st.caption("💡 These word combinations are frequently used together in Russian")
        
        if 'regional_variations' in data and data['regional_variations']:
            st.markdown("#### Regional Variations")
            st.write(data['regional_variations'])
            st.caption("→ How this word might differ across Russian-speaking regions")
        
        # Memory aids
        st.markdown("#### Memory Aids")
        st.info("💭 **Remember:** Practice with the case examples above - they show real usage patterns!")
        st.info("🔄 **Tip:** Try creating your own sentences using different cases to reinforce learning")

def get_enhanced_russian_content(english_word, section, subsection):
    """Enhanced version that requests English translations for grammatical forms"""
    prompt = f"""
    You are a Russian language expert helping MBBS students learn medical and general Russian vocabulary with comprehensive grammatical analysis.
    
    Context: This is for the "{section}" section, specifically "{subsection}" subsection.
    English word: "{english_word}"
    
    Please provide ONLY a valid JSON response with this exact structure:
    {{
        "russian_word": "Russian translation with pronunciation in parentheses",
        "part_of_speech": "noun/verb/adjective/adverb/etc.",
        "gender": "masculine/feminine/neuter/not applicable",
        "pronunciation_stress": "Word with stress mark (е́, а́, etc.) and phonetic guide",
        "etymology": "Brief origin/etymology of the word",
        
        "formal_sentence": "A formal sentence using this word in Russian context",
        "formal_sentence_english": "English translation of the formal sentence",
        "formal_pos": "Part of speech used in formal sentence",
        "formal_grammar": "Grammatical form used (case, number, tense, etc.)",
        
        "informal_sentence": "An informal/casual sentence using this word",
        "informal_sentence_english": "English translation of the informal sentence",
        "informal_pos": "Part of speech used in informal sentence",
        "informal_grammar": "Grammatical form used (case, number, tense, etc.)",
        
        "question": "A question in Russian that would naturally use this word",
        "question_english": "English translation of the question",
        "question_pos": "Part of speech used in question",
        "question_grammar": "Grammatical form used (case, number, tense, etc.)",
        
        "answer": "An appropriate answer to that question in Russian",
        "answer_english": "English translation of the answer",
        "answer_pos": "Part of speech used in answer",
        "answer_grammar": "Grammatical form used (case, number, tense, etc.)",
        
        "cases": {{
            "nominative": "Russian form with example sentence and English translation",
            "accusative": "Russian form with example sentence and English translation",
            "genitive": "Russian form with example sentence and English translation",
            "dative": "Russian form with example sentence and English translation",
            "instrumental": "Russian form with example sentence and English translation",
            "prepositional": "Russian form with example sentence and English translation"
        }},
        
        "verb_conjugation": {{
            "infinitive": "Infinitive form if verb",
            "present": {{
                "я": "я form",
                "ты": "ты form",
                "он_она": "он/она form",
                "мы": "мы form",
                "вы": "вы form",
                "они": "они form"
            }},
            "past": {{
                "masculine": "past masculine form",
                "feminine": "past feminine form",
                "neuter": "past neuter form",
                "plural": "past plural form"
            }},
            "future": {{
                "я": "я future form",
                "ты": "ты future form",
                "он_она": "он/она future form",
                "мы": "мы future form",
                "вы": "вы future form",
                "они": "они future form"
            }},
            "aspect": "perfective/imperfective/both",
            "perfective_partner": "perfective form if imperfective",
            "imperfective_partner": "imperfective form if perfective"
        }},
        
        "mood": {{
            "imperative": "Command form (делай! делайте!)",
            "conditional": "Conditional form (would do)"
        }},
        
        "plural_forms": {{
            "nominative_plural": "Plural nominative form with English explanation",
            "genitive_plural": "Plural genitive form with English explanation",
            "other_plurals": "Other important plural forms with English explanations"
        }},
        
        "prefixes_suffixes": {{
            "common_prefixes": "Common prefixes that change meaning with examples",
            "common_suffixes": "Common suffixes that change meaning with examples",
            "related_words": "Words formed with prefixes/suffixes with English translations"
        }},
        
        "negation": {{
            "negative_form": "How word behaves in negative sentences with English explanation",
            "negative_example": "Example of word in negative sentence",
            "negative_example_english": "English translation of negative example"
        }},
        
        "common_collocations": [
            "Common phrase 1 with this word (with English translation)",
            "Common phrase 2 with this word (with English translation)",
            "Common phrase 3 with this word (with English translation)"
        ],
        
        "regional_variations": "Any regional differences in usage",
        "difficulty_level": "beginner/intermediate/advanced"
    }}
    
    IMPORTANT: 
    1. For each case declension, provide the Russian form AND a short example with English translation
    2. For plural forms, include English explanations of usage
    3. For negative examples, always include English translations
    4. For collocations, include English translations in parentheses
    5. Make all examples relevant to MBBS students in Russia
    6. Focus on practical, medical-relevant usage
    """
    
    # Use the same error handling as the original function
    # but with enhanced prompt for better English translations
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Same JSON parsing logic as original...
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith('{') or in_json:
                    in_json = True
                    json_lines.append(line)
                    if line.strip().endswith('}') and line.count('}') >= line.count('{'):
                        break
            response_text = '\n'.join(json_lines)
        
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_text = response_text[start_idx:end_idx]
            content = json.loads(json_text)
            
            required_keys = ["russian_word", "part_of_speech", "formal_sentence", "informal_sentence", "question", "answer"]
            if all(key in content for key in required_keys):
                return content
            else:
                raise ValueError("Missing required keys in response")
        else:
            raise ValueError("No valid JSON found in response")
            
    except Exception as e:
        st.error(f"Error generating enhanced content: {str(e)}")
        # Return the same fallback as original function
        return get_enhanced_russian_content(english_word, section, subsection)

def create_theme_toggle():
    """Create the theme toggle component"""
    toggle_html = f"""
    <style>
    .theme-toggle-container {{
        display: flex;
        justify-content: center;
        padding: 10px 0;
        margin-bottom: 20px;
    }}
    
    .toggle {{
        width: 38px;
        height: 38px;
        border-radius: 8px;
        display: grid;
        place-items: center;
        cursor: pointer;
        line-height: 1;
        background-color: {'#1e1e1e' if st.session_state.get('dark_mode', False) else '#f0f2f6'};
        border: 2px solid {'#333' if st.session_state.get('dark_mode', False) else '#e1e5e9'};
        transition: all 0.3s ease;
    }}
    
    .toggle:hover {{
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    .input {{
        display: none;
    }}
    
    .icon {{
        grid-column: 1 / 1;
        grid-row: 1 / 1;
        transition: transform 500ms;
        line-height: 0.1;
    }}
    
    .icon--moon {{
        transition-delay: 200ms;
        color: #b4b4b4;
        transform: {'rotate(360deg) scale(0)' if st.session_state.get('dark_mode', False) else 'scale(1)'};
    }}
    
    .icon--sun {{
        color: #ffa500;
        transform: {'scale(1) rotate(360deg)' if st.session_state.get('dark_mode', False) else 'scale(0)'};
        transition-delay: {'200ms' if st.session_state.get('dark_mode', False) else '0ms'};
    }}
    </style>
    
    <div class="theme-toggle-container">
        <div class="toggle" id="theme-toggle" onclick="toggleTheme()">
            <div class="icon icon--moon">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    width="24"
                    height="24"
                >
                    <path
                        fill-rule="evenodd"
                        d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z"
                        clip-rule="evenodd"
                    ></path>
                </svg>
            </div>
            <div class="icon icon--sun">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    width="24"
                    height="24"
                >
                    <path
                        d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z"
                    ></path>
                </svg>
            </div>
        </div>
    </div>
    
    <script>
    let toggleClicked = false;
    
    function toggleTheme() {{
        if (toggleClicked) return; // Prevent multiple rapid clicks
        toggleClicked = true;
        
        // Toggle the dark mode state
        const currentMode = {str(st.session_state.get('dark_mode', False)).lower()};
        
        // Create a hidden form to submit the toggle action
        const form = document.createElement('form');
        form.method = 'POST';
        form.style.display = 'none';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'theme_toggle';
        input.value = currentMode ? 'light' : 'dark';
        
        form.appendChild(input);
        document.body.appendChild(form);
        
        // Reset the flag after a short delay
        setTimeout(() => {{
            toggleClicked = false;
        }}, 1000);
        
        // Trigger Streamlit rerun by clicking a hidden button
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            data: {{
                key: 'theme_toggle_clicked',
                value: !currentMode
            }}
        }}, '*');
    }}
    </script>
    """
    
    return toggle_html

def apply_theme():
    """Apply dark or light theme based on session state"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    if st.session_state.dark_mode:
        # Dark mode styles (unchanged)
        st.markdown("""
        <style>
        /* Dark Mode Styles */
        .stApp {
            background-color: #0e1117 !important;
            color: #fafafa !important;
        }
        
        /* SIDEBAR - More specific selectors */
        .css-1d391kg, .css-1lcbmhc, .css-17eq0hr, section[data-testid="stSidebar"] {
            background-color: #262730 !important;
        }
        
        .css-1d391kg .stMarkdown, 
        .css-1lcbmhc .stMarkdown,
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] .element-container {
            color: #fafafa !important;
            background-color: transparent !important;
        }
        
        /* Sidebar headers - all levels */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] h5,
        section[data-testid="stSidebar"] h6,
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2, 
        section[data-testid="stSidebar"] .stMarkdown h3,
        section[data-testid="stSidebar"] .stMarkdown h4,
        section[data-testid="stSidebar"] .stMarkdown h5,
        section[data-testid="stSidebar"] .stMarkdown h6 {
            color: #fafafa !important;
        }
        
        /* Sidebar text elements */
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] strong,
        section[data-testid="stSidebar"] .stMarkdown strong,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div,
        section[data-testid="stSidebar"] label {
            color: #fafafa !important;
        }
        
        /* Sidebar buttons */
        section[data-testid="stSidebar"] .stButton > button {
            background-color: #ff6b6b !important;
            color: white !important;
            border: none !important;
        }
        
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }
        
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
            background-color: #1e1e1e !important;
            color: #fafafa !important;
            border: 1px solid #333 !important;
        }
        
        /* More aggressive targeting for all secondary buttons in sidebar */
        section[data-testid="stSidebar"] button[kind="secondary"],
        section[data-testid="stSidebar"] .stButton button[kind="secondary"],
        section[data-testid="stSidebar"] .element-container button[kind="secondary"],
        section[data-testid="stSidebar"] div[data-testid="column"] button[kind="secondary"] {
            background-color: #1e1e1e !important;
            color: #fafafa !important;
            border: 1px solid #333 !important;
        }
        
        /* Target all buttons that might be in the sidebar columns */
        section[data-testid="stSidebar"] .stButton button,
        section[data-testid="stSidebar"] button {
            background-color: #1e1e1e !important;
            color: #fafafa !important;
            border: 1px solid #333 !important;
        }
        
        /* Override for primary buttons */
        section[data-testid="stSidebar"] .stButton button[kind="primary"],
        section[data-testid="stSidebar"] button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }
        
        /* Sidebar inputs */
        section[data-testid="stSidebar"] .stTextInput input,
        section[data-testid="stSidebar"] .stSelectbox select,
        section[data-testid="stSidebar"] .stNumberInput input {
            background-color: #1e1e1e !important;
            color: #fafafa !important;
            border: 1px solid #333 !important;
        }
        
        /* Sidebar widget labels */
        section[data-testid="stSidebar"] .stTextInput label,
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stNumberInput label,
        section[data-testid="stSidebar"] .stSlider label {
            color: #fafafa !important;
        }
        
        /* Main content area */
        .main .block-container {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Cards and containers */
        div[data-testid="stContainer"] {
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        
        /* Metrics */
        div[data-testid="metric-container"] {
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
        }
        
        div[data-testid="metric-container"] > div {
            color: #fafafa !important;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #ff6b6b;
            color: white;
            border: none;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #ff5252;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
        }
        
        /* Primary button */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background-color: #1e1e1e !important;
            color: #fafafa !important;
            border: 1px solid #333;
        }
        
        .streamlit-expanderContent {
            background-color: #262730 !important;
            border: 1px solid #333;
        }
        
        /* Progress bars */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        }
        
        /* Text inputs and selectboxes */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            background-color: #1e1e1e !important;
            color: #fafafa !important;
            border: 1px solid #333 !important;
        }
        
        /* Success/Info/Error messages */
        .stSuccess {
            background-color: #1e3a1e !important;
            border: 1px solid #4caf50 !important;
            color: #fafafa !important;
        }
        
        .stInfo {
            background-color: #1e2a3a !important;
            border: 1px solid #2196f3 !important;
            color: #fafafa !important;
        }
        
        .stError {
            background-color: #3a1e1e !important;
            border: 1px solid #f44336 !important;
            color: #fafafa !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1e1e1e;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #fafafa;
            background-color: #262730;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #ff6b6b !important;
            color: white !important;
        }
        
        /* Markdown headers */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            color: #fafafa;
        }
        
        /* Code blocks */
        .stCode {
            background-color: #1e1e1e;
            border: 1px solid #333;
        }
        
        /* Force dark theme on all text elements */
        * {
            scrollbar-width: thin;
            scrollbar-color: #666 #1e1e1e;
        }
        
        *::-webkit-scrollbar {
            width: 8px;
        }
        
        *::-webkit-scrollbar-track {
            background: #1e1e1e;
        }
        
        *::-webkit-scrollbar-thumb {
            background-color: #666;
            border-radius: 4px;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light mode styles with very slight orange background
        st.markdown("""
        <style>
        /* Light Mode Styles with slight orange tint */
        .stApp {
            background-color: #fffef8 !important;
            color: #262730;
        }
        
        /* Main content area */
        .main .block-container {
            background-color: #fffef8;
            color: #262730;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #faf7f2 !important;
        }
        
        /* Sidebar text and headers */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2, 
        section[data-testid="stSidebar"] .stMarkdown h3 {
            color: #262730 !important;
        }
        
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] strong,
        section[data-testid="stSidebar"] .stMarkdown strong {
            color: #262730 !important;
        }
        
        /* Sidebar buttons */
        section[data-testid="stSidebar"] .stButton > button {
            background-color: #ff6b6b !important;
            color: white !important;
        }
        
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
            background-color: #ffffff !important;
            color: #262730 !important;
            border: 1px solid #e1e5e9 !important;
        }
        
        /* Cards and containers */
        div[data-testid="stContainer"] {
            background-color: #fefcf7;
            border: 1px solid #e1e5e9;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Metrics */
        div[data-testid="metric-container"] {
            background-color: #fefcf7;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #ff6b6b;
            color: white;
            border: none;
            border-radius: 8px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            background-color: #ff5252;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
        }
        
        /* Primary button */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        
        /* Progress bars */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        }
        </style>
        """, unsafe_allow_html=True)

def add_theme_toggle_to_sidebar():
    """Add theme toggle to the top of sidebar using the fancy toggle component"""
    # Create a custom container that puts toggle and button on same line
    st.sidebar.markdown("""
    <style>
    .theme-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 10px 0 20px 0;
        gap: 15px;
    }
    
    .theme-toggle-wrapper {
        flex: 0 0 auto;
    }
    
    .theme-button-wrapper {
        flex: 1;
        display: flex;
        justify-content: flex-end;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create columns for the toggle and button
    col1, col2 = st.sidebar.columns([1, 2])
    
    with col1:
        # Display the fancy toggle
        toggle_html = create_theme_toggle()
        st.markdown(toggle_html, unsafe_allow_html=True)
    
    with col2:
        # Check for theme toggle clicks using a unique key
        toggle_key = f"theme_toggle_{st.session_state.get('dark_mode', False)}"
        
        if st.button("Change Theme", key=f"change_{toggle_key}", 
                    type="secondary", 
                    help="Toggle between light and dark mode",
                    use_container_width=True):
            st.session_state.dark_mode = not st.session_state.get('dark_mode', False)
            st.rerun()
    
    st.sidebar.markdown("---")
   
def updated_main():
    """Updated main function using JSON database with direct subsection navigation and dark mode toggle"""
    
    # Apply theme first
    apply_theme()
    
    st.title("🏥 Russian Learning App for All Soon-to-Be Doctor")
    
    # Subtitle with heart button next to it
    subtitle_col, button_col = st.columns([3, 1])
    with subtitle_col:
        st.markdown("Comprehensive app for all your needs")
    
    # Load database and check if successful
    if not load_vocabulary_database():
        st.error("❌ Failed to load vocabulary database. Please check your db.json file.")
        return
    
    # Initialize session state
    if 'current_word_data' not in st.session_state:
        st.session_state.current_word_data = None
    if 'selected_section' not in st.session_state:
        st.session_state.selected_section = None
    if 'selected_subsection' not in st.session_state:
        st.session_state.selected_subsection = None
    
    # Initialize progress from JSON structure
    initialize_progress_from_json()
    
    # Get sections from JSON
    sections = get_sections_from_json()
    
    if not sections:
        st.error("❌ No sections found in database.")
        return
    
    # Section definitions for organization
    section_data = {
        'Core Subjects': {
            'icon': '🧬',
            'subsections': ['Anatomy', 'Physiology', 'Biochemistry', 'Pathology', 'Pharmacology', 'Microbiology', 'Forensic Medicine', 'Cell Biology']
        },
        'Clinical & Hospital Environment': {
            'icon': '🏥',
            'subsections': ['Clinical Skills & Tools', 'Symptoms & Signs', 'Hospital Departments', 'Medical Procedures', 'Community Medicine']
        },
        'Communication & Ethics': {
            'icon': '💬',
            'subsections': ['Doctor-Patient Communication', 'Medical Ethics & Law', 'Medical Abbreviations', 'Medical Research Terms', 'Medical Jargon vs Layman\'s Terms']
        },
        'Environmental Health & Botany': {
            'icon': '🌱',
            'subsections': ['Flowers & Trees', 'Environmental Science', 'Weather & Seasons']
        },
        'Life Abroad / General Living': {
            'icon': '🏠',
            'subsections': ['Housing & Accommodation', 'Transportation', 'Shopping & Food', 'Conversation with Strangers']
        },
        'Academic & Study Support': {
            'icon': '📚',
            'subsections': ['Maths & Biostatistics', 'History', 'Psychology']
        },
        'Emergency Situations': {
            'icon': '🚨',
            'subsections': ['Medical Emergencies', 'Non-Medical Emergencies']
        }
    }
    
    # Subsection icons for sidebar only (not used in main buttons)
    subsection_icons = {
        # Core Subjects
        'Anatomy': '🫀', 'Physiology': '⚡', 'Biochemistry': '🧪', 'Pathology': '🔬',
        'Pharmacology': '💊', 'Microbiology': '🦠', 'Forensic Medicine': '⚖️', 'Cell Biology': '🔬',
        
        # Clinical & Hospital
        'Clinical Skills & Tools': '🩺', 'Symptoms & Signs': '🤒', 'Hospital Departments': '🏥',
        'Medical Procedures': '⚕️', 'Community Medicine': '👥',
        
        # Communication & Ethics  
        'Doctor-Patient Communication': '👨‍⚕️', 'Medical Ethics & Law': '⚖️', 'Medical Abbreviations': '📝',
        'Medical Research Terms': '📊', 'Medical Jargon vs Layman\'s Terms': '🗣️',
        
        # Environmental Health & Botany
        'Flowers & Trees': '🌸', 'Environmental Science': '🌍', 'Weather & Seasons': '🌤️',
        
        # Life Abroad
        'Housing & Accommodation': '🏠', 'Transportation': '🚌', 'Shopping & Food': '🛒',
        'Conversation with Strangers': '👋',
        
        # Academic Support
        'Maths & Biostatistics': '📊', 'History': '📜', 'Psychology': '🧠',
        
        # Emergency
        'Medical Emergencies': '🚑', 'Non-Medical Emergencies': '🚨'
    }
    

    
    # GIF URLs for subsections
    subsection_gifs = {
        # Core Subjects
        'Anatomy': 'https://github.com/SavvyGaikwad/media/blob/main/Physiology.gif?raw=true',
        'Physiology': 'https://github.com/SavvyGaikwad/media/blob/main/Anatomy.gif?raw=true',
        'Biochemistry': 'https://github.com/SavvyGaikwad/media/blob/main/Biochemistry.gif?raw=true',
        'Pathology': 'https://github.com/SavvyGaikwad/media/blob/main/Pathology.gif?raw=true',
        'Pharmacology': 'https://github.com/SavvyGaikwad/media/blob/main/Pharmacology.gif?raw=true',
        'Microbiology': 'https://github.com/SavvyGaikwad/media/blob/main/Microbiology.gif?raw=true',
        'Forensic Medicine': 'https://github.com/SavvyGaikwad/media/blob/main/Forensic%20Medicine.gif?raw=true',
        'Cell Biology': 'https://github.com/SavvyGaikwad/media/blob/main/Cell%20Biology.gif?raw=true',
        
        # Clinical & Hospital Environment
        'Clinical Skills & Tools': 'https://github.com/SavvyGaikwad/media/blob/main/clinic.gif?raw=true',
        'Hospital Departments': 'https://github.com/SavvyGaikwad/media/blob/main/Hospital.gif?raw=true',
        'Medical Procedures': 'https://github.com/SavvyGaikwad/media/blob/main/Medical%20Procedures.gif?raw=true',
        'Community Medicine': 'https://github.com/SavvyGaikwad/media/blob/main/Community%20Medicine.gif?raw=true',
        
        # Communication & Ethics
        'Doctor-Patient Communication': 'https://github.com/SavvyGaikwad/media/blob/main/conversation.gif?raw=true',
        'Medical Ethics & Law': 'https://github.com/SavvyGaikwad/media/blob/main/Medical%20Ethics%20%26%20Law.gif?raw=true',
        'Medical Abbreviations': 'https://github.com/SavvyGaikwad/media/blob/main/Abbreviations.gif?raw=true',
        'Medical Research Terms': 'https://github.com/SavvyGaikwad/media/blob/main/research.gif?raw=true',
        'Medical Jargon vs Layman\'s Terms': 'https://github.com/SavvyGaikwad/media/blob/main/Medical%20Jargon%20vs%20Layman\'s%20Terms.gif?raw=true',
        
        # Environmental Health & Botany
        'Flowers & Trees': 'https://github.com/SavvyGaikwad/media/blob/main/sunflower.gif?raw=true',
        'Environmental Science': 'https://github.com/SavvyGaikwad/media/blob/main/green-planet.gif?raw=true',
        'Weather & Seasons': 'https://github.com/SavvyGaikwad/media/blob/main/seasons.gif?raw=true',
        
        # Life Abroad / General Living
        'Housing & Accommodation': 'https://github.com/SavvyGaikwad/media/blob/main/home.gif?raw=true',
        'Transportation': 'https://github.com/SavvyGaikwad/media/blob/main/train.gif?raw=true',
        'Shopping & Food': 'https://github.com/SavvyGaikwad/media/blob/main/shopping-bag.gif?raw=true',
        'Conversation with Strangers': 'https://github.com/SavvyGaikwad/media/blob/main/three-friends.gif?raw=true',
        
        # Academic & Study Support
        'Maths & Biostatistics': 'https://github.com/SavvyGaikwad/media/blob/main/math.gif?raw=true',
        'History': 'https://github.com/SavvyGaikwad/media/blob/main/history.gif?raw=true',
        'Psychology': 'https://github.com/SavvyGaikwad/media/blob/main/emotions.gif?raw=true',
        
        # Emergency Situations
        'Medical Emergencies': 'https://github.com/SavvyGaikwad/media/blob/main/ambulance.gif?raw=true',
        'Non-Medical Emergencies': 'https://github.com/SavvyGaikwad/media/blob/main/earthquake.gif?raw=true'
    }
    
    # ============ SIDEBAR SETUP ============
    # Add theme toggle at the top of sidebar
    add_theme_toggle_to_sidebar()
    
    # Progress section (only show if subsection is selected)
    if st.session_state.selected_subsection:
        selected_section = st.session_state.selected_section
        selected_subsection = st.session_state.selected_subsection
        
        # Show progress for current subsection
        progress_key = f"{selected_section}_{selected_subsection}"
        
        # Ensure the progress key exists
        if progress_key not in st.session_state.subsection_progress:
            st.session_state.subsection_progress[progress_key] = set()
        
        used_count = len(st.session_state.subsection_progress[progress_key])
        total_words = count_words_in_subsection(selected_section, selected_subsection)
        max_words = min(total_words, 3)  # Cap at 3 or total available words
        
        # Calculate progress (0 to 1)
        progress = min(used_count / max_words, 1.0) if max_words > 0 else 0
        
        st.sidebar.markdown("### 📊 Current Subsection Progress")
        
        # Progress bar with color coding
        if progress == 1.0:
            st.sidebar.success(f"✅ Completed!")
        else:
            st.sidebar.progress(progress)
        
        st.sidebar.caption(f"{used_count}/{max_words} words learned ({total_words} available)")
        
        # Show progress for all subsections in current section
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### 📈 {selected_section} - All Progress")
        
        for subsection in sections[selected_section].keys():
            progress_key = f"{selected_section}_{subsection}"
            
            # Ensure the progress key exists
            if progress_key not in st.session_state.subsection_progress:
                st.session_state.subsection_progress[progress_key] = set()
            
            used_count = len(st.session_state.subsection_progress[progress_key])
            total_words = count_words_in_subsection(selected_section, subsection)
            max_words = min(total_words, 3)
            
            # Calculate progress (0 to 1)
            progress = min(used_count / max_words, 1.0) if max_words > 0 else 0
            
            # Display GIF or fallback to icon for subsection
            if subsection in subsection_gifs:
                # Create columns for GIF and text
                gif_col, text_col = st.sidebar.columns([1, 3])
                with gif_col:
                    st.image(subsection_gifs[subsection], width=30)
                with text_col:
                    # Style current subsection differently
                    if subsection == st.session_state.selected_subsection:
                        st.markdown(f"**🔸 {subsection}**")
                    else:
                        st.markdown(f"• {subsection}")
            else:
                # Fallback to icon if no GIF available
                sub_icon = subsection_icons.get(subsection, '📌')
                # Style current subsection differently
                if subsection == st.session_state.selected_subsection:
                    st.sidebar.markdown(f"**🔸 {sub_icon} {subsection}**")
                else:
                    st.sidebar.markdown(f"• {sub_icon} {subsection}")
            
            # Mini progress bar
            if progress == 1.0:
                st.sidebar.success(f"✅ Done ({used_count}/{max_words})")
            else:
                st.sidebar.progress(progress)
                st.sidebar.caption(f"{used_count}/{max_words}")
            
            st.sidebar.markdown("")
        
        # Overall section progress
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🏆 Overall Section Progress")
        
        total_learned = 0
        total_possible = 0
        
        for subsection in sections[selected_section].keys():
            progress_key = f"{selected_section}_{subsection}"
            if progress_key in st.session_state.subsection_progress:
                subsection_learned = len(st.session_state.subsection_progress[progress_key])
                total_words = count_words_in_subsection(selected_section, subsection)
                max_words = min(total_words, 3)
                total_learned += min(subsection_learned, max_words)
                total_possible += max_words
        
        overall_progress = total_learned / total_possible if total_possible > 0 else 0
        
        # Color-coded overall progress
        if overall_progress == 1.0:
            st.sidebar.success("🎉 Section Complete!")
            st.sidebar.progress(overall_progress)
        elif overall_progress >= 0.75:
            st.sidebar.info("🔥 Almost there!")
            st.sidebar.progress(overall_progress)
        else:
            st.sidebar.progress(overall_progress)
        
        st.sidebar.write(f"Section total: {total_learned}/{total_possible} words")
        
        # Achievement badges
        if overall_progress == 1.0:
            st.sidebar.markdown("🏆 **Section Master Badge Earned!**")
        elif overall_progress >= 0.5:
            st.sidebar.markdown("🥉 **Half-way Hero!**")
        
        # Reset options
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🔄 Reset Current", help="Reset current subsection"):
                progress_key = f"{selected_section}_{selected_subsection}"
                st.session_state.subsection_progress[progress_key] = set()
                st.session_state.current_word_data = None
                st.rerun()
        
        with col2:
            if st.button("🗑️ Reset All", help="Reset entire section"):
                for subsection in sections[selected_section].keys():
                    progress_key = f"{selected_section}_{subsection}"
                    st.session_state.subsection_progress[progress_key] = set()
                st.session_state.current_word_data = None
                st.rerun()
        
        # Add flip card functionality if it exists
        try:
            add_flip_card_to_sidebar()
        except NameError:
            # Function doesn't exist, skip silently
            pass
    else:
        # Empty sidebar when no subsection is selected
        pass
    
    # ============ MAIN CONTENT AREA ============
    if not st.session_state.selected_subsection:
        # Welcome screen with direct subsection selection
        st.markdown("### 👋 Welcome to Your Russian Learning Journey!")
        st.markdown("Choose any topic below to start learning immediately:")
        st.markdown("---")
        
        # Display sections with subsection buttons
        for section_name, section_info in section_data.items():
            if section_name in sections:  # Only show sections that exist in database
                
                # Section header
                st.markdown(f"### **{section_info['icon']} {section_name}**")
                
                # Get available subsections for this section
                available_subsections = [sub for sub in section_info['subsections'] if sub in sections[section_name]]
                
                if available_subsections:
                    # Special handling for Core Subjects - display in 2 rows of 4 each
                    if section_name == 'Core Subjects':
                        # First row - first 4 subsections
                        first_row_subsections = available_subsections[:4]
                        if first_row_subsections:
                            cols1 = st.columns(len(first_row_subsections))
                            for idx, subsection in enumerate(first_row_subsections):
                                with cols1[idx]:
                                    # Display GIF above button if available (centered)
                                    if subsection in subsection_gifs:
                                        # Center the image using columns
                                        _, center_col, _ = st.columns([1, 2, 1])
                                        with center_col:
                                            st.image(subsection_gifs[subsection], width=100)
                                    else:
                                        # Display subsection name as header if no GIF (centered)
                                        st.markdown(f"<div style='text-align: center'><strong>{subsection}</strong></div>", unsafe_allow_html=True)
                                    
                                    # Get progress info for styling
                                    progress_key = f"{section_name}_{subsection}"
                                    if progress_key not in st.session_state.subsection_progress:
                                        st.session_state.subsection_progress[progress_key] = set()
                                    
                                    used_count = len(st.session_state.subsection_progress[progress_key])
                                    total_words = count_words_in_subsection(section_name, subsection)
                                    max_words = min(total_words, 3)
                                    progress = min(used_count / max_words, 1.0) if max_words > 0 else 0
                                    
                                    # Create button text with shortened name and progress indication
                                    # Create button text with full name and progress indication
                                    display_name = subsection
                                    button_text = display_name
                                    if progress == 1.0:
                                        button_text += " ✅"
                                    elif progress > 0:
                                        button_text += f" ({used_count}/{max_words})"
                                    
                                    # Button for subsection selection
                                    if st.button(button_text, key=f"direct_select_{section_name}_{subsection}", use_container_width=True):
                                        st.session_state.selected_section = section_name
                                        st.session_state.selected_subsection = subsection
                                        st.session_state.current_word_data = None
                                        st.rerun()
                        
                        # Second row - remaining subsections
                        second_row_subsections = available_subsections[4:]
                        if second_row_subsections:
                            cols2 = st.columns(len(second_row_subsections))
                            for idx, subsection in enumerate(second_row_subsections):
                                with cols2[idx]:
                                    # Display GIF above button if available (centered)
                                    if subsection in subsection_gifs:
                                        # Center the image using columns
                                        _, center_col, _ = st.columns([1, 2, 1])
                                        with center_col:
                                            st.image(subsection_gifs[subsection], width=100)
                                    else:
                                        # Display subsection name as header if no GIF (centered)
                                        st.markdown(f"<div style='text-align: center'><strong>{subsection}</strong></div>", unsafe_allow_html=True)
                                    
                                    # Get progress info for styling
                                    progress_key = f"{section_name}_{subsection}"
                                    if progress_key not in st.session_state.subsection_progress:
                                        st.session_state.subsection_progress[progress_key] = set()
                                    
                                    used_count = len(st.session_state.subsection_progress[progress_key])
                                    total_words = count_words_in_subsection(section_name, subsection)
                                    max_words = min(total_words, 3)
                                    progress = min(used_count / max_words, 1.0) if max_words > 0 else 0
                                    
                                    # Create button text with shortened name and progress indication
                                    # Create button text with full name and progress indication
                                    display_name = subsection
                                    button_text = display_name
                                    if progress == 1.0:
                                        button_text += " ✅"
                                    elif progress > 0:
                                        button_text += f" ({used_count}/{max_words})"
                                    
                                    # Button for subsection selection
                                    if st.button(button_text, key=f"direct_select_{section_name}_{subsection}", use_container_width=True):
                                        st.session_state.selected_section = section_name
                                        st.session_state.selected_subsection = subsection
                                        st.session_state.current_word_data = None
                                        st.rerun()
                    else:
                        # Default layout for other sections - single row
                        # Create subsection display with GIFs and buttons
                        num_subsections = len(available_subsections)
                        
                        # Create columns for subsections
                        cols = st.columns(num_subsections)
                        
                        for idx, subsection in enumerate(available_subsections):
                            with cols[idx]:
                                # Display GIF above button if available (centered)
                                if subsection in subsection_gifs:
                                    # Center the image using columns
                                    _, center_col, _ = st.columns([1, 2, 1])
                                    with center_col:
                                        st.image(subsection_gifs[subsection], width=100)
                                else:
                                    # Display subsection name as header if no GIF (centered)
                                    st.markdown(f"<div style='text-align: center'><strong>{subsection}</strong></div>", unsafe_allow_html=True)
                                
                                # Get progress info for styling
                                progress_key = f"{section_name}_{subsection}"
                                if progress_key not in st.session_state.subsection_progress:
                                    st.session_state.subsection_progress[progress_key] = set()
                                
                                used_count = len(st.session_state.subsection_progress[progress_key])
                                total_words = count_words_in_subsection(section_name, subsection)
                                max_words = min(total_words, 3)
                                progress = min(used_count / max_words, 1.0) if max_words > 0 else 0
                                
                                # Create button text with shortened name and progress indication
                                # Create button text with full name and progress indication
                                display_name = subsection
                                button_text = display_name
                                if progress == 1.0:
                                    button_text += " ✅"
                                elif progress > 0:
                                    button_text += f" ({used_count}/{max_words})"
                                
                                # Button for subsection selection
                                if st.button(button_text, key=f"direct_select_{section_name}_{subsection}", use_container_width=True):
                                    st.session_state.selected_section = section_name
                                    st.session_state.selected_subsection = subsection
                                    st.session_state.current_word_data = None
                                    st.rerun()
                
                st.markdown("---")
    
    else:
        # Learning interface
        selected_section = st.session_state.selected_section
        selected_subsection = st.session_state.selected_subsection
        section_info = section_data[selected_section]
        
        # Breadcrumb navigation with GIF display
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            # Display GIF if available, otherwise use icon
            if selected_subsection in subsection_gifs:
                # Create a sub-column layout for GIF + text
                gif_col, text_col = st.columns([1, 3])
                with gif_col:
                    st.image(subsection_gifs[selected_subsection], width=80)
                with text_col:
                    st.markdown(f"### {selected_subsection}")
            else:
                # Fallback to icon if no GIF available
                icon = subsection_icons.get(selected_subsection, '📌')
                st.markdown(f"### {icon} {selected_subsection}")
        with col2:
            st.markdown("")
        with col3:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.selected_section = None
                st.session_state.selected_subsection = None
                st.session_state.current_word_data = None
                st.rerun()
        
        st.markdown("---")
        
        # Get next word button
        if st.button("🎲 Get Next Word", use_container_width=True):
            progress_key = f"{selected_section}_{selected_subsection}"
            
            # Ensure progress key exists
            if progress_key not in st.session_state.subsection_progress:
                st.session_state.subsection_progress[progress_key] = set()
            
            used_words_for_subsection = st.session_state.subsection_progress[progress_key]
            total_words = count_words_in_subsection(selected_section, selected_subsection)
            max_words = min(total_words, 3)
            
            # Check if we've reached the word limit for this subsection
            if len(used_words_for_subsection) >= max_words:
                st.balloons()  # Celebration animation
                st.success(f"🎉 Congratulations! You've completed {max_words} words from '{selected_subsection}'!")
                
                # Show completion stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words Mastered", max_words)
                with col2:
                    st.metric("Total Available", total_words) 
                with col3:
                    completion_rate = (max_words / total_words * 100) if total_words > 0 else 0
                    st.metric("Completion Rate", f"{completion_rate:.1f}%")
                
                st.info("🚀 **Next Steps:**\n- Reset this subsection to practice again\n- Choose a different subsection to continue learning\n- Try a new section for broader vocabulary!")
                
                # Show recommended next subsection from same section
                current_subsections = list(sections[selected_section].keys())
                current_index = current_subsections.index(selected_subsection)
                if current_index < len(current_subsections) - 1:
                    next_subsection = current_subsections[current_index + 1]
                    next_icon = subsection_icons.get(next_subsection, '📌')
                    
                    # Quick access button to next subsection (using full name in navigation)
                    if st.button(f"🚀 Continue with {next_icon} {next_subsection}", type="secondary", use_container_width=True):
                        st.session_state.selected_subsection = next_subsection
                        st.session_state.current_word_data = None
                        st.rerun()
                else:
                    st.info(f"🎊 You've completed all subsections in '{selected_section}'!")
            else:
                # Get random unused word
                try:
                    current_word = get_random_word_from_subsection(selected_section, selected_subsection)
                    
                    if current_word:
                        st.session_state.subsection_progress[progress_key].add(current_word)
                        
                        # Show loading spinner while generating content
                        with st.spinner("Loading..."):
                            try:
                                russian_content = get_enhanced_russian_content(current_word, selected_section, selected_subsection)
                                
                                st.session_state.current_word_data = {
                                    'english_word': current_word,
                                    'section': selected_section,
                                    'subsection': selected_subsection,
                                    **russian_content
                                }
                            except Exception as e:
                                st.error(f"Failed to generate content: {str(e)}")
                                st.session_state.current_word_data = None
                    else:
                        # No more words available
                        st.info(f"🔄 All words from '{selected_subsection}' have been used!")
                        st.info("Reset this subsection or choose a different one to continue learning.")
                except NameError as e:
                    st.error(f"Function not found: {str(e)}")
                    st.info("Please ensure all required functions are properly defined.")
        
        # Display current word data with enhanced presentation
        if st.session_state.current_word_data:
            data = st.session_state.current_word_data
            
            st.markdown("---")
            
            # Word display with enhanced styling
            st.markdown("### 🎯 Current Word")
            col_en, col_ru = st.columns(2)
            
            with col_en:
                st.markdown("#### 🇬🇧 English")
                st.markdown(f"# **{data['english_word'].title()}**")
            
            with col_ru:
                st.markdown("#### 🇷🇺 Russian")
                st.markdown(f"# **{data.get('russian_word', 'Not available')}**")
            
            # Usage examples with grammatical information
            st.markdown("---")
            st.markdown("### 📝 Usage Examples")
            
            # Formal usage
            with st.expander("🎩 Formal Usage", expanded=True):
                st.markdown(f"**Russian:** {data.get('formal_sentence', 'Not available')}")
                if 'formal_sentence_english' in data:
                    st.markdown(f"**English:** {data['formal_sentence_english']}")
                if 'formal_grammar' in data:
                    st.info(f"**Grammar:** {data.get('formal_pos', 'N/A')} - {data['formal_grammar']}")
            
            # Informal usage
            with st.expander("😊 Informal Usage", expanded=True):
                st.markdown(f"**Russian:** {data.get('informal_sentence', 'Not available')}")
                if 'informal_sentence_english' in data:
                    st.markdown(f"**English:** {data['informal_sentence_english']}")
                if 'informal_grammar' in data:
                    st.info(f"**Grammar:** {data.get('informal_pos', 'N/A')} - {data['informal_grammar']}")
            
            # Question and Answer
            with st.expander("❓ Question & Answer Practice", expanded=True):
                st.markdown(f"**Question (Russian):** {data.get('question', 'Not available')}")
                if 'question_english' in data:
                    st.markdown(f"**Question (English):** {data['question_english']}")
                if 'question_grammar' in data:
                    st.info(f"**Question Grammar:** {data.get('question_pos', 'N/A')} - {data['question_grammar']}")
                
                st.markdown(f"**Answer (Russian):** {data.get('answer', 'Not available')}")
                if 'answer_english' in data:
                    st.markdown(f"**Answer (English):** {data['answer_english']}")
                if 'answer_grammar' in data:
                    st.info(f"**Answer Grammar:** {data.get('answer_pos', 'N/A')} - {data['answer_grammar']}")
            
            # Comprehensive grammatical analysis
            st.markdown("---")
            try:
                display_grammatical_info(data)
            except NameError:
                st.info("Grammatical analysis function not available.")
                # Show basic word info if available
                if 'russian_word' in data:
                    st.markdown("### 📚 Word Information")
                    st.markdown(f"**English:** {data['english_word']}")
                    st.markdown(f"**Russian:** {data['russian_word']}")
                    st.markdown(f"**Section:** {data['section']}")
                    st.markdown(f"**Subsection:** {data['subsection']}")

if __name__ == "__main__":
    updated_main()
