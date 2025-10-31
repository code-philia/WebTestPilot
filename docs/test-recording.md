# Test Recording Feature PRD

## Overview
Record user interactions in browser, capture video, and convert to structured test steps using multi-modal LLM.

## Core Requirements

### 1. Recording Interface
- **Start/Stop Recording**: Button in test editor toolbar
- **Visual Feedback**: Red recording indicator with timer
- **Browser Integration**: Connect to existing CDP browser session
- **Audio/Video Capture**: Record screen at 15fps with interaction metadata

### 2. Data Collection
- **Video Stream**: H.264 compressed video (1920x1080)
- **Interaction Events**: Click coordinates, keyboard input, scroll events
- **DOM Snapshots**: Element selectors and page state changes
- **Timing Data**: Timestamps for all interactions

### 3. AI Processing Pipeline
- **Video Analysis**: Send frames to multi-modal LLM (Qwen-VL)
- **Action Extraction**: Convert visual interactions to natural language actions
- **Step Generation**: Create action/expectation pairs
- **Format Output**: Generate TestAction[] compatible with existing models

### 4. Integration Points
- **Test Editor**: Insert generated steps into current test
- **CDP Integration**: Use existing browser connection
- **LLM Client**: Leverage existing LocalModel/Qwen-VL client
- **File Storage**: Save recordings for replay/debugging

## Technical Specifications

### Video Processing
```typescript
interface RecordingData {
  videoBlob: Blob;
  interactions: InteractionEvent[];
  duration: number;
  timestamp: number;
}
```

### LLM Prompt Template
```
Analyze this browser recording and extract test steps:
Format: [{"action": "click login button", "expectedResult": "login form appears"}]
Focus on user intent and expected outcomes.
```

### API Integration
- Extend `cli.py` with `--process-recording` flag
- Add recording processing to `main.py`
- New BAML function for video-to-steps conversion

## Success Criteria
- Convert 30-second recording to test steps in <10 seconds
- 85% accuracy in action recognition
- Seamless integration with existing test editor
- Support for common interactions: click, type, scroll, navigate

## MVP Scope
- Basic click/type/scroll recognition
- Single-tab recording
- Manual start/stop control
- English language output only