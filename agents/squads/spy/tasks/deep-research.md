# Task: Deep Player Research

**Task ID:** deep-research
**Version:** 2.0.0
**Status:** active
**Responsible Executor:** Agent (@research-head)
**Execution Type:** Agent
**Model:** Sonnet (requires pattern analysis and synthesis)
**Haiku Eligible:** NO - requires deep content analysis

## Input
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `handle` | string | Yes | YouTube channel or Instagram handle |
| `platform` | enum | Yes | `youtube` or `instagram` |
| `depth` | enum | No | `standard` (10 videos) or `comprehensive` (30 videos) |

## Output
| Artifact | Location | Description |
|----------|----------|-------------|
| Raw Data | `outputs/spy/raw/{platform}/{handle}_*.json` | API response data |
| Transcripts | `outputs/spy/transcripts/{platform}/{handle}_*.md` | Annotated transcripts |
| Analysis | `outputs/spy/analysis/players/{handle}_analysis.md` | Pattern analysis |
| Deep Dive Report | `outputs/spy/reports/deep-dives/{handle}_deep-dive.md` | Final report |

## Veto Conditions
- STOP if no API access (check credentials first)
- STOP if channel has <10 public videos
- STOP if engagement data unavailable
- STOP if pattern count <3 (not enough data)

## Acceptance Criteria
- [ ] 10+ videos analyzed with full metrics
- [ ] Transcripts extracted and annotated
- [ ] Patterns validated (3+ occurrences each)
- [ ] Comment analysis completed (50+ comments)
- [ ] Swipe file entries created
- [ ] Knowledge base updated
- [ ] Report saved to outputs/spy/reports/

---

## Objective
Analyze a player in depth to extract replicable patterns.

## Estimated Time
2-4 hours per player

---

## PHASE 1: COLLECTION (30-60 min)

### 1.1 Basic Data
```bash
# YouTube - list channel videos
curl "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={ID}&type=video&maxResults=50&order=date&key=$YOUTUBE_API_KEY"

# YouTube - video statistics
curl "https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet,contentDetails&id={IDs}&key=$YOUTUBE_API_KEY"
```

### 1.2 What to Collect
- [ ] Last 30-50 videos/posts
- [ ] Metrics for each (views, likes, comments)
- [ ] Publication dates
- [ ] Video durations
- [ ] Full titles and descriptions
- [ ] Tags/hashtags

### 1.3 Save to
```
outputs/spy/raw/{platform}/{handle}_videos_{date}.json
outputs/spy/raw/{platform}/{handle}_stats_{date}.json
```

---

## PHASE 2: SELECTION (15 min)

### 2.1 Identify Top Performers
Sort by:
1. Views (volume)
2. Engagement rate (likes/views)
3. Comments (discussion)

### 2.2 Select for Deep Analysis
- [ ] Top 5 by views
- [ ] Top 3 by engagement
- [ ] 2 most recent (current trend)
= **10 pieces to analyze**

---

## PHASE 3: TRANSCRIPTION (60-90 min)

### 3.1 For Each Selected Video
- [ ] Download/extract transcript (subtitles or Whisper)
- [ ] Fix obvious errors
- [ ] Mark important timestamps

### 3.2 Format
```markdown
# Transcript: {title}

**Channel:** {name}
**URL:** {link}
**Views:** {number}
**Duration:** {time}

---

[00:00] HOOK: {first 10 seconds}

[00:10] INTRO: {problem presentation}

[02:00] CONTENT: {development}

[15:00] CTA: {call to action}

---

## Observations
- What worked:
- What didn't work:
- Pattern identified:
```

### 3.3 Save to
```
outputs/spy/transcripts/{platform}/{handle}_{title-slug}_{date}.md
```

---

## PHASE 4: PATTERN ANALYSIS (60 min)

### 4.1 Titles
For each title, answer:
- Which formula does it use? (provocation, urgency, number, curiosity, hype)
- What's the promise?
- Has number/time?
- Character count?

### 4.2 Hooks (first 10 seconds)
- What type? (provocation, result, curiosity, authority)
- Does it capture attention?
- What's the exact first sentence?

### 4.3 Structure
- How long until value delivery?
- Has practical demo?
- Where's the CTA placed?
- What's the rhythm? (cuts, music, etc)

### 4.4 Language
- Tone: formal/informal/sarcastic/energetic?
- Repeated words?
- Catchphrases?
- Niche slang?

### 4.5 Save Analysis to
```
outputs/spy/analysis/players/{handle}_analysis_{date}.md
```

---

## PHASE 5: COMMENT ANALYSIS (30 min)

### 5.1 Collect Top 50 Comments from Top Videos

### 5.2 Categorize
- Praise (what do they praise?)
- Questions (what didn't they understand?)
- Requests (what do they want more of?)
- Criticism (what do they complain about?)

### 5.3 Insights
- What does the audience REALLY want?
- What content to request in comments?
- Gaps the player isn't covering

---

## PHASE 6: SYNTHESIS (30 min)

### 6.1 Consolidate Findings
```markdown
# Synthesis: @{handle}

## Content DNA
- Tone:
- Preferred format:
- Average duration:
- Frequency:

## Formulas That Work
1. Title: {pattern}
2. Hook: {pattern}
3. Structure: {pattern}

## Effect Phrases (Swipe File)
- "{phrase 1}"
- "{phrase 2}"
- "{phrase 3}"

## What the Audience Wants
1.
2.
3.

## Application for Us
| Their Pattern | How to Adapt |
|---------------|--------------|
| | |
```

---

## PHASE 7: FINAL REPORT (30 min)

### 7.1 Create Deep Dive
Use template in: `outputs/spy/reports/deep-dives/`

### 7.2 Update Framework
If new pattern discovered, add to:
`squads/spy/data/viral-content-framework.md`

---

## FINAL CHECKLIST

- [ ] Raw data saved to raw/
- [ ] 10 pieces transcribed
- [ ] Pattern analysis complete
- [ ] Comments analyzed
- [ ] Synthesis written
- [ ] Deep Dive published
- [ ] Framework updated (if applicable)

---

## DELIVERABLES

1. `raw/{handle}_*.json` - raw data
2. `transcripts/{handle}_*.md` - transcripts
3. `analysis/players/{handle}_analysis.md` - analysis
4. `reports/deep-dives/{handle}_deep-dive.md` - final report

---

*Deep Research Task v2.0*
