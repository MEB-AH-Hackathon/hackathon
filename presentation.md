# VAERS Analyzer
## Bridging Patient Language and Medical Documentation

AI-powered analysis system for the Vaccine Adverse Event Reporting System (VAERS), the national early warning system established in 1990 to detect vaccine safety concerns. Our system maps patient language to medical terminology, revealing hidden patterns in adverse event reports submitted to CDC and FDA.

**Key Features:**
- `Real-time Claude AI agents`
- `VAERS & FDA integration`
- `MCP Protocol`

---

## The Real Problem
### Same Symptom, Different Words

<div align="center">

### **"I had a fever"**
### vs
### **"Pyrexia"**
### vs
### **"Temperature of 101°F"**

</div>

> ⚠️ **All the same thing** - but how do we know?

---

## Who Needs This?

### 🏥 **Public Health Officials**
> "Are 1,000 people reporting the same new symptom using different words?"

### 👤 **Individual Patients**
> "Did anyone else experience what I'm experiencing? Is this a documented issue?"

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
### 💉 Injection Site Reactions

| **VAERS Says** | **FDA Says** |
|----------------|--------------|
| "Injection site vasculitis" | "cellulitis", "injection site reactions" |
| "Vaccination site joint pain" | "injection site reactions", "arthralgia" |
| "Injection site joint movement impairment" | "injection site reactions", "joint stiffness" |

---

## Real Examples: Allergic Reactions
### 🤧 Allergic Symptoms

| **VAERS Says** | **FDA Says** |
|----------------|--------------|
| "Throat tightness" | "anaphylaxis", "swelling" |
| "Pharyngeal swelling" | "anaphylaxis", "angioedema" |
| "Swelling face" | "facial swelling", "angioedema" |

---

## Real Examples: Systemic Reactions
### 🤒 Whole-Body Symptoms

| **VAERS Says** | **FDA Says** |
|----------------|--------------|
| "Body temperature increased" | "fever", "pyrexia" |
| "Feeling hot" | "fever", "flushing" |
| "Burning sensation" | "injection site burning", "pain" |

---

## What This Enables
### 📊 For Public Health Monitoring

**Before:**
- 500 reports of "throat tightness"
- 300 reports of "pharyngeal swelling"
- 200 reports of "difficulty swallowing"

**After:**
> 🚨 **1,000 reports of potential anaphylaxis**

---

## What This Enables
### 🔍 For Individual Patients

**Your Symptom**: "My face feels hot and tingly"

**Find Similar Reports:**
- "Facial flushing" (243 reports)
- "Face hot" (189 reports)
- "Burning sensation face" (97 reports)
- "Facial paraesthesia" (156 reports)

> ✅ **Total: 685 people with similar experiences**

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
```
"Injection site vasculitis" → "cellulitis", "injection site reactions"
"Body temperature increased" → "fever", "pyrexia"
"Throat tightness" → "anaphylaxis", "swelling"
```

### Real-Time Agent Analysis
```
New symptom: "My arm feels like it's on fire"
↓
Claude Agent analyzes in context
↓
Maps to: "injection site burning", "pain", "inflammation"
```

---

## How You Use It - On Our Website

### Option 1: Browse & Analyze Real Reports
View actual VAERS reports from the CDC/FDA database with AI analysis:

**VAERS 2548069** | 77 years • female • SC
- **Vaccines:** VARZOS
- **Symptoms:** Injection site pain, Injection site erythema, Injection site nodule
- **Onset:** 4 days after vaccination

Click "View Details" to see:
- Which symptoms match FDA adverse events
- AI-powered symptom mapping
- Similar reports and patterns

---

## Option 2: Check Any VAERS Report

### Enter a VAERS ID
1. **Input any VAERS ID** (e.g., 2548069)
2. **System fetches** the official report
3. **AI analyzes** all symptoms
4. **Shows matches** to FDA adverse events

### Example Output
```
VAERS Report 2548069:
✅ "Injection site pain" → Matches FDA: "injection site pain"
✅ "Injection site erythema" → Matches FDA: "injection site erythema"
✅ "Injection site nodule" → Matches FDA: "injection site nodule"
```

---

## Option 3: Describe Your Own Symptoms

### Natural Language Input
Type symptoms in your own words:
> "I have a headache and my arm is really sore where I got the shot. Also feeling super tired."

### System Response
```
Your symptoms analyzed:
✅ "headache" → Known FDA adverse event
✅ "arm is really sore" → Maps to "injection site pain"
✅ "super tired" → Maps to "fatigue"

Similar reports found: 2,847 people reported this combination
```

---

## Real-Time Agent in Action

### When You Enter Something New
Your input: "It feels like ants crawling under my skin"

**Claude Agent Process:**
1. No exact match in pre-processed mappings
2. Agent analyzes: sensation + location + description
3. Medical knowledge: "formication" / "paraesthesia"
4. Checks FDA terms: Maps to "tingling", "numbness"
5. Returns: "Unusual sensation, possibly nerve-related"

---

## Impact: Finding Hidden Patterns

### Case Study: Myocarditis

> ⚠️ Different ways patients reported heart inflammation:
> - "Chest pain" (2,341 reports)
> - "Heart inflammation" (892 reports)
> - "Myocarditis" (423 reports)
> - "Pericarditis" (198 reports)
> - "Heart racing" (1,205 reports)

> ✅ **Total: 5,059 potential cardiac events**
> (vs 423 if only counting "myocarditis")

---

## Key Achievements

### Data Quality
- **Standardized** naming across systems
- **Cleaned** data types (Y/N → true/false)
- **Validated** symptom mappings using real reports
- **Connected** patient language to medical terms

### Hybrid AI Approach
- **Pre-processed mappings** for common symptoms
- **Real-time agents** for novel descriptions
- **Context-aware** analysis using full symptom text
- **No training required** - works out of the box

---

## Featured on Our Website

### Browse Real VAERS Reports
Explore actual reports with AI-powered analysis:

**VAERS 2547741** | 58 years • male • CA
- **Vaccines:** COVID19
- **Symptoms:** Pain, Magnetic resonance imaging abnormal, Arthritis reactive... +3 more

**VAERS 2547788** | 59 years • female • GA
- **Vaccines:** COVID19-2
- **Symptoms:** Influenza virus test negative, Malaise, Streptococcus test negative... +3 more

---

## System Information

### About VAERS
- **1990**: VAERS Established
- **CDC + FDA**: Co-Managed By
- **Public Access**: Open Reporting
- National early warning system

### Our Innovation
- **Real-time Claude AI agents**
- **VAERS & FDA integration**
- **MCP Protocol**
- **Symptom mapping system**

---

## Future Vision

### Systematic Mapping Framework
- **Standardized evaluation criteria** for symptom similarity
- **Confidence scoring** for mapping quality
- **Hierarchical symptom taxonomies** (specific → general)
- **Cross-validation** against multiple medical ontologies

### Evaluation & Quality Metrics
- **Inter-rater reliability** for mapping consistency
- **Sensitivity/specificity** testing for agent performance
- **Benchmark datasets** for systematic comparison
- **Automated quality assessment** of new mappings

---

# Questions & Discussion

## Thank you!

**Try it yourself at: https://vaers-analyzer.vercel.app/**