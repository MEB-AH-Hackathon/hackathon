<style>
/* Presentation Styling */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: 0;
    padding: 20px;
}

.slide {
    background: white;
    margin: 20px auto;
    padding: 40px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-width: 900px;
}

h1 {
    color: #2c3e50;
    font-size: 2.5em;
    text-align: center;
    margin-bottom: 10px;
    border-bottom: 3px solid #3498db;
    padding-bottom: 10px;
}

h2 {
    color: #1a4d7a;
    font-size: 2em;
    margin-top: 30px;
    margin-bottom: 20px;
    border-left: 4px solid #3498db;
    padding-left: 15px;
}

h3 {
    color: #34495e;
    font-size: 1.3em;
    margin-top: 25px;
    margin-bottom: 15px;
}

.big-text {
    font-size: 2.5em;
    text-align: center;
    margin: 40px 0;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 10px;
    border-left: 5px solid #e74c3c;
}

.mapping-table {
    width: 100%;
    font-size: 1.5em;
    margin: 20px 0;
    border-collapse: collapse;
}

.mapping-table td {
    padding: 15px;
    border-bottom: 1px solid #ecf0f1;
    vertical-align: middle;
}

.mapping-table td:first-child {
    background: #ecf0f1;
    font-weight: bold;
    color: #2c3e50;
    border-radius: 5px 0 0 5px;
}

.mapping-table td:last-child {
    background: #e8f4fd;
    font-weight: bold;
    color: #1e3a8a;
    border-radius: 0 5px 5px 0;
}

.mapping-table td:nth-child(2) {
    text-align: center;
    font-size: 2em;
    color: #3498db;
}

.code-block {
    background: #2c3e50;
    color: #ecf0f1;
    padding: 20px;
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    font-size: 1.1em;
    margin: 20px 0;
    overflow-x: auto;
}

.highlight-box {
    background: #fef3c7;
    border: 2px solid #f59e0b;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    color: #92400e;
    font-weight: bold;
}

.success-box {
    background: #dbeafe;
    border: 2px solid #3b82f6;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    color: #1e40af;
    font-weight: bold;
}

.warning-box {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
}

.emoji-large {
    font-size: 1.5em;
}

blockquote {
    background: #f8f9fa;
    border-left: 4px solid #6c757d;
    margin: 20px 0;
    padding: 15px 20px;
    font-style: italic;
    color: #495057;
}

ul li {
    margin: 8px 0;
    padding-left: 5px;
}

.center {
    text-align: center;
}

.two-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin: 20px 0;
}

.process-step {
    background: #e3f2fd;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    border-left: 4px solid #2196f3;
}

.demo-output {
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 15px;
    font-family: monospace;
    margin: 15px 0;
}

hr {
    border: none;
    height: 2px;
    background: linear-gradient(to right, #3498db, #e74c3c);
    margin: 40px 0;
}
</style>

# Understanding Vaccine Adverse Events
## Making Sense of Real-World Reports

---

## The Real Problem

### Same Symptom, Different Words

<div class="big-text">
<strong>"I had a fever"</strong><br/>
vs<br/>
<strong>"Pyrexia"</strong><br/>
vs<br/>
<strong>"Temperature of 101°F"</strong>
</div>

<div class="highlight-box center">
<strong>All the same thing</strong> - but how do we know?
</div>

---

## Who Needs This?

<div class="two-column">
<div>

### <span class="emoji-large">🏥</span> Public Health Officials
> "Are 1,000 people reporting the same new symptom using different words?"

</div>
<div>

### <span class="emoji-large">👤</span> Individual Patients  
> "Did anyone else experience what I'm experiencing? Is this a documented issue?"

</div>
</div>

---

## The Current Reality

### VAERS Reports Use Natural Language
- "My arm was sore and red"
- "Injection site erythema with pain"
- "Redness and soreness at shot location"

### FDA Documents Use Medical Terms
- "Injection site reactions"
- "Erythema"
- "Local reactions"

**How do we connect these?**

---

## Real Examples from Our Data

### <span class="emoji-large">💉</span> Injection Site Reactions

<table class="mapping-table">
<tr>
<td><strong>VAERS Says</strong></td>
<td>→</td>
<td><strong>FDA Says</strong></td>
</tr>
<tr>
<td>"Injection site vasculitis"</td>
<td>→</td>
<td>"cellulitis", "injection site reactions"</td>
</tr>
<tr>
<td>"Vaccination site joint pain"</td>
<td>→</td>
<td>"injection site reactions", "arthralgia"</td>
</tr>
<tr>
<td>"Injection site joint movement impairment"</td>
<td>→</td>
<td>"injection site reactions", "joint stiffness"</td>
</tr>
</table>

---

## Real Examples: Allergic Reactions

### <span class="emoji-large">🤧</span> Allergic Symptoms

<table class="mapping-table">
<tr>
<td><strong>VAERS Says</strong></td>
<td>→</td>
<td><strong>FDA Says</strong></td>
</tr>
<tr>
<td>"Throat tightness"</td>
<td>→</td>
<td>"anaphylaxis", "swelling"</td>
</tr>
<tr>
<td>"Pharyngeal swelling"</td>
<td>→</td>
<td>"anaphylaxis", "angioedema"</td>
</tr>
<tr>
<td>"Swelling face"</td>
<td>→</td>
<td>"facial swelling", "angioedema"</td>
</tr>
</table>

---

## Real Examples: Systemic Reactions

### <span class="emoji-large">🤒</span> Whole-Body Symptoms

<table class="mapping-table">
<tr>
<td><strong>VAERS Says</strong></td>
<td>→</td>
<td><strong>FDA Says</strong></td>
</tr>
<tr>
<td>"Body temperature increased"</td>
<td>→</td>
<td>"fever", "pyrexia"</td>
</tr>
<tr>
<td>"Feeling hot"</td>
<td>→</td>
<td>"fever", "flushing"</td>
</tr>
<tr>
<td>"Burning sensation"</td>
<td>→</td>
<td>"injection site burning", "pain"</td>
</tr>
</table>

---

## What This Enables

### 📊 For Public Health Monitoring

**Before**: 
- 500 reports of "throat tightness"
- 300 reports of "pharyngeal swelling"  
- 200 reports of "difficulty swallowing"

**After**:
- **1,000 reports of potential anaphylaxis** 🚨

---

## What This Enables

### 🔍 For Individual Patients

**Your Symptom**: "My face feels hot and tingly"

**Find Similar Reports**:
- "Facial flushing" (243 reports)
- "Face hot" (189 reports)
- "Burning sensation face" (97 reports)
- "Facial paraesthesia" (156 reports)

**Total: 685 people with similar experiences**

---

## Our Solution: Two-Part AI System

### 🔧 Pre-Processing: Building the Foundation
- **Extract** FDA adverse events from package inserts
- **Create mappings** for common symptoms using Claude AI
- **Build crosswalk** between patient language and medical terms
- **Validate** mappings with real VAERS reports

### ⚡ Real-Time Processing: Handle Anything New
- **MCP Claude agents** analyze new symptoms on the spot
- **No pre-mapping needed** - works with any input
- **Context-aware** - uses symptom text for better matching
- **Instant results** - no waiting for batch processing

---

## How It Works

### Pre-Processed Mappings
<div class="code-block">
"Injection site vasculitis" → "cellulitis", "injection site reactions"
"Body temperature increased" → "fever", "pyrexia"
"Throat tightness" → "anaphylaxis", "swelling"
</div>

### Real-Time Agent Analysis
<div class="code-block">
New symptom: "My arm feels like it's on fire"
↓
Claude Agent analyzes in context
↓
Maps to: "injection site burning", "pain", "inflammation"
</div>

---

## The Technology Stack

### Hybrid Approach
1. **Pre-processed mappings** for speed and consistency
2. **MCP/Claude agents** for flexibility and new symptoms
3. **Context analysis** using full symptom descriptions
4. **Subset of VAERS data** for demo purposes
5. **Real FDA documents** for ground truth

---

## User Interface: Find Your People

### Search Your Symptoms
*[Screenshot: Search interface]*

- **Natural language search**: "arm hurts and red"
- **Medical term search**: "injection site erythema"
- **Find both** automatically

### See Similar Reports
*[Screenshot: Similar reports list]*

- **Grouped by similarity** not exact matches
- **Severity indicators** (hospitalized, ER visit, etc.)
- **Time patterns** (when symptoms appeared)

---

## Impact: Finding Hidden Patterns

### Case Study: Myocarditis

<div class="highlight-box">
Different ways patients reported heart inflammation:
<ul>
<li>"Chest pain" (2,341 reports)</li>
<li>"Heart inflammation" (892 reports)</li>
<li>"Myocarditis" (423 reports)</li>
<li>"Pericarditis" (198 reports)</li>
<li>"Heart racing" (1,205 reports)</li>
</ul>
</div>

<div class="success-box center">
<strong>Total: 5,059 potential cardiac events</strong><br/>
(vs 423 if only counting "myocarditis")
</div>

---

## Making Data Accessible

### Before Our System
- **Medical professionals**: Use medical terms
- **Patients**: Use everyday language
- **Researchers**: Miss connections
- **Public health**: Delayed pattern recognition

### After Our System
- **Everyone**: Can find relevant reports
- **Patterns**: Emerge faster
- **Communities**: Form naturally
- **Response**: More timely and accurate

---

## Technical Implementation

### Four Core Data Files
1. **FDA adverse events** - What we expect
2. **VAERS reports** - What people experience  
3. **Symptom mappings** - How they connect
4. **Report categorization** - Match analysis

### Smart Matching Algorithm
- Exact medical term matches
- Synonym recognition
- Context-based matching
- Severity alignment

---

## Live Demo Scenarios

### Scenario 1: "I'm Worried About My Symptoms"
1. User searches: "dizzy and nauseous after shot"
2. System finds: Vertigo, dizziness, nausea reports
3. Shows: 1,847 similar experiences
4. Provides: This is a known symptom

### Scenario 2: "Public Health Monitoring"
1. Official views: Real-time symptom dashboard
2. System alerts: Unusual cluster of "throat tightness"
3. Investigation: Maps to potential allergic reactions
4. Action: Issue guidance to healthcare providers

---


## Call to Action

### For Public Health Officials
- **Better surveillance** with unified terminology
- **Faster pattern detection** across language barriers
- **Community insights** from patient experiences

### For Patients
- **Find other people** with similar experiences
- **Understand your symptoms** in context
- **Know whether** your symptoms are already documented clinically

---

## Questions & Discussion

### Try It Yourself
- **Demo URL**: [Application URL]
- **GitHub**: [Repository URL](https://github.com/MEB-AH-Hackathon/hackathon)

**Thank you!**