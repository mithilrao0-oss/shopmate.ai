import { useState } from "react";
import "./ReelEditor.css";

const SCENE_LABELS = ["Hook", "Product", "Benefit", "Call to action"];

// Same limits as the backend validator (backend/app/agent/reel_script.py).
const MAX_VOICEOVER_WORDS = 20;
const MAX_ON_SCREEN_WORDS = 7;

function countWords(text) {
  return text.trim() ? text.trim().split(/\s+/).length : 0;
}

/**
 * Scene-by-scene editor for a structured reel script.
 * Give it a new `key` for every generation so the hashtag box resets.
 */
export default function ReelEditor({ payload, onChange, estimatedSeconds }) {
  const [hashtagText, setHashtagText] = useState(
    (payload.hashtags ?? []).join(" ")
  );

  function updateScene(index, field, value) {
    const scenes = payload.scenes.map((scene, sceneIndex) =>
      sceneIndex === index ? { ...scene, [field]: value } : scene
    );

    onChange({ ...payload, scenes });
  }

  function updateHashtags(text) {
    setHashtagText(text);

    onChange({
      ...payload,
      hashtags: text.split(/[\s,]+/).filter(Boolean),
    });
  }

  return (
    <div className="reel-editor" aria-label="Reel script editor">
      <p className="reel-meta">
        {payload.scenes.length} scenes
        {estimatedSeconds != null && (
          <> &middot; about {estimatedSeconds} seconds when spoken</>
        )}
      </p>

      {payload.scenes.map((scene, index) => {
        const voiceoverWords = countWords(scene.voiceover);
        const screenWords = countWords(scene.on_screen_text);

        return (
          <div className="reel-scene" key={index}>
            <h4>
              Scene {index + 1}
              {SCENE_LABELS[index] ? ` \u00b7 ${SCENE_LABELS[index]}` : ""}
            </h4>

            <label htmlFor={`reel-voiceover-${index}`}>
              Voiceover
              <span
                className={
                  voiceoverWords > MAX_VOICEOVER_WORDS ? "reel-count over" : "reel-count"
                }
              >
                {voiceoverWords}/{MAX_VOICEOVER_WORDS} words
              </span>
            </label>
            <textarea
              id={`reel-voiceover-${index}`}
              rows={2}
              value={scene.voiceover}
              onChange={(event) => updateScene(index, "voiceover", event.target.value)}
            />

            <label htmlFor={`reel-screen-${index}`}>
              On-screen text
              <span
                className={
                  screenWords > MAX_ON_SCREEN_WORDS ? "reel-count over" : "reel-count"
                }
              >
                {screenWords}/{MAX_ON_SCREEN_WORDS} words
              </span>
            </label>
            <input
              id={`reel-screen-${index}`}
              type="text"
              value={scene.on_screen_text}
              onChange={(event) =>
                updateScene(index, "on_screen_text", event.target.value)
              }
            />
          </div>
        );
      })}

      <div className="reel-scene">
        <h4>Instagram post</h4>

        <label htmlFor="reel-caption">Caption</label>
        <textarea
          id="reel-caption"
          rows={3}
          value={payload.caption}
          onChange={(event) => onChange({ ...payload, caption: event.target.value })}
        />

        <label htmlFor="reel-hashtags">Hashtags (3 to 5, separated by spaces)</label>
        <input
          id="reel-hashtags"
          type="text"
          value={hashtagText}
          onChange={(event) => updateHashtags(event.target.value)}
        />
      </div>
    </div>
  );
}
