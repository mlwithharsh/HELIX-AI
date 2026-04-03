import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

const TAG_OPTIONS = ['helpful', 'confusing', 'too long', 'supportive', 'clear'];

const FeedbackBar = ({ interactionId, onSubmit, disabled }) => {
  const [selectedTags, setSelectedTags] = useState([]);
  const [submitted, setSubmitted] = useState(false);

  const toggleTag = (tag) => {
    setSelectedTags((current) =>
      current.includes(tag) ? current.filter((item) => item !== tag) : [...current, tag]
    );
  };

  const handleSubmit = (vote) => {
    const apiTags = selectedTags.map(t => t.replace(' ', '_'));
    onSubmit(interactionId, vote, apiTags);
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="flex items-center space-x-2 py-2">
        <div className="w-1.5 h-1.5 rounded-full bg-solace-purple animate-pulse" />
        <span className="text-xs text-text-muted italic">Thanks — adapting to your preferences</span>
      </div>
    );
  }

  return (
    <div className="space-y-3 max-w-[80%] animate-fade-in">
      <div className="flex items-center gap-3">
        <button
          type="button"
          disabled={disabled}
          onClick={() => handleSubmit('up')}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-[#eef3ec] border border-[#d4dfd0] text-[#5a7252] text-xs font-semibold transition-all duration-300 hover:bg-[#e2eddf] hover:shadow-sm active:scale-95"
        >
          <ThumbsUp className="w-3.5 h-3.5" />
          <span>Helpful</span>
        </button>
        <button
          type="button"
          disabled={disabled}
          onClick={() => handleSubmit('down')}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-[#f5ede6] border border-[#e4d8cc] text-[#8b6f56] text-xs font-semibold transition-all duration-300 hover:bg-[#f0e6db] hover:shadow-sm active:scale-95"
        >
          <ThumbsDown className="w-3.5 h-3.5" />
          <span>Needs Work</span>
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {TAG_OPTIONS.map((tag) => (
          <button
            key={tag}
            type="button"
            onClick={() => toggleTag(tag)}
            className={`px-2.5 py-1 rounded-full text-[11px] font-medium border transition-all duration-200 ${
              selectedTags.includes(tag)
                ? 'bg-[#eef3ec] border-[#b8ccb0] text-[#4a6542]'
                : 'bg-white/60 border-black/5 text-text-muted hover:bg-[#f6f1e8] hover:text-text-secondary'
            }`}
          >
            {tag}
          </button>
        ))}
      </div>
    </div>
  );
};

export default FeedbackBar;
