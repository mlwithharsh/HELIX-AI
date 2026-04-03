from cryptography.fernet import Fernet
import uuid
from datetime import datetime


class MemoryManager:
    def __init__(self, key=None):
        if key is None:
            key = Fernet.generate_key()
        self.fernet = Fernet(key)
        self.history = []
        self.long_term_memories = []
        self.user_profile = {
            "preferences": [],
            "behavioral_patterns": [],
            "emotional_history": [],
        }
        self.reflections = []
        self.execution_logs = []
        self.max_short_term_memories = 20
        self.max_long_term_memories = 50
        self.max_reflections = 30
        self.max_execution_logs = 100

    def add_memory(self, user, helix, session_id=None, analysis=None, reward=None, reflection=None):
        try:
            if not session_id:
                session_id = str(uuid.uuid4())

            if not user or not helix:
                print("Warning: Empty user or helix input, skipping memory storage")
                return

            encrypted_user = self.fernet.encrypt(user.encode()).decode()
            encrypted_helix = self.fernet.encrypt(helix.encode()).decode()
            timestamp = datetime.now().isoformat()

            memory_item = {
                "session": session_id,
                "user": encrypted_user,
                "helix": encrypted_helix,
                "timestamp": timestamp,
                "analysis": analysis or {},
                "reward": reward,
            }
            self.history.append(memory_item)
            self._trim_history()
            self._update_profile(user, analysis or {})

            importance = self.score_importance(user, helix, analysis or {}, reward)
            if importance >= 0.6:
                self.long_term_memories.append({
                    "session": session_id,
                    "user": user,
                    "helix": helix,
                    "timestamp": timestamp,
                    "analysis": analysis or {},
                    "reward": reward,
                    "importance": importance,
                })
                self.long_term_memories = sorted(
                    self.long_term_memories,
                    key=lambda item: (item.get("importance", 0), item.get("timestamp", "")),
                    reverse=True,
                )[: self.max_long_term_memories]

            if reflection:
                self.reflections.append(reflection)
                self.reflections = self.reflections[-self.max_reflections :]
        except Exception as e:
            print(f"Memory storage error: {e}")
            try:
                self.history.append({
                    "session": session_id or str(uuid.uuid4()),
                    "user": user,
                    "helix": helix,
                    "timestamp": datetime.now().isoformat(),
                    "encrypted": False,
                    "analysis": analysis or {},
                    "reward": reward,
                })
                self._trim_history()
            except Exception as fallback_error:
                print(f"Fallback memory storage also failed: {fallback_error}")

    def _trim_history(self):
        if len(self.history) > self.max_short_term_memories:
            self.history = self.history[-self.max_short_term_memories :]

    def _update_profile(self, user_text, analysis):
        lowered = (user_text or "").lower()
        preference_markers = ["i like", "i love", "i prefer", "my favorite", "i enjoy"]
        if any(marker in lowered for marker in preference_markers):
            self.user_profile["preferences"].append(user_text.strip())
            self.user_profile["preferences"] = self.user_profile["preferences"][-10:]

        if len((user_text or "").split()) > 20:
            self.user_profile["behavioral_patterns"].append("User tends to send detailed messages.")
        elif len((user_text or "").split()) <= 5:
            self.user_profile["behavioral_patterns"].append("User sometimes prefers concise prompts.")

        self.user_profile["behavioral_patterns"] = list(dict.fromkeys(self.user_profile["behavioral_patterns"]))[-10:]

        emotion = (analysis or {}).get("emotion")
        sentiment = (analysis or {}).get("sentiment")
        if emotion or sentiment:
            self.user_profile["emotional_history"].append({
                "emotion": emotion or "neutral",
                "sentiment": sentiment or "neutral",
                "timestamp": datetime.now().isoformat(),
            })
            self.user_profile["emotional_history"] = self.user_profile["emotional_history"][-20:]

    def score_importance(self, user_text, helix_text, analysis, reward):
        score = 0.2
        score += min(len((user_text or "").split()) / 40, 0.2)
        if (analysis or {}).get("emotion") not in (None, "", "neutral"):
            score += 0.15
        if (analysis or {}).get("sentiment") in ("positive", "negative"):
            score += 0.1
        if reward is not None:
            score += max(min(reward, 1), -1) * 0.15
        if any(token in (user_text or "").lower() for token in ["remember", "important", "always", "prefer", "goal"]):
            score += 0.2
        if len((helix_text or "").split()) > 40:
            score += 0.05
        return max(0.0, min(score, 1.0))

    def get_context_text(self, session_id=None):
        try:
            if session_id:
                session_history = [msg for msg in self.history if msg["session"] == session_id]
            else:
                session_history = self.history

            context_parts = []
            for msg in session_history:
                try:
                    if msg.get("encrypted", True):
                        user_text = self.fernet.decrypt(msg["user"].encode()).decode()
                        helix_text = self.fernet.decrypt(msg["helix"].encode()).decode()
                    else:
                        user_text = msg["user"]
                        helix_text = msg["helix"]

                    context_parts.append(f"User: {user_text}\nHelix: {helix_text}")
                except Exception as msg_error:
                    print(f"Error processing message {msg.get('timestamp', 'unknown')}: {msg_error}")
                    continue

            return "\n".join(context_parts)
        except Exception as e:
            print(f"Memory retrieval error: {e}")
            return ""

    def get_relevant_memories(self, query=None, limit=3):
        if not self.long_term_memories:
            return []
        if not query:
            return self.long_term_memories[:limit]

        query_terms = set(query.lower().split())
        ranked = []
        for memory in self.long_term_memories:
            content = f"{memory.get('user', '')} {memory.get('helix', '')}".lower()
            overlap = len(query_terms.intersection(content.split()))
            ranked.append((overlap + memory.get("importance", 0), memory))

        ranked.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in ranked[:limit]]

    def get_user_profile_summary(self):
        preferences = "; ".join(self.user_profile["preferences"][-3:]) or "No explicit preferences stored yet."
        patterns = "; ".join(self.user_profile["behavioral_patterns"][-3:]) or "No stable behavior patterns yet."
        recent_emotions = [entry.get("emotion", "neutral") for entry in self.user_profile["emotional_history"][-5:]]
        emotional_trend = ", ".join(recent_emotions) if recent_emotions else "neutral"
        return {
            "preferences": preferences,
            "behavioral_patterns": patterns,
            "emotional_trend": emotional_trend,
        }

    def get_emotional_summary(self):
        recent = self.user_profile["emotional_history"][-5:]
        if not recent:
            return {"dominant_emotion": "neutral", "dominant_sentiment": "neutral"}

        emotions = {}
        sentiments = {}
        for item in recent:
            emotions[item["emotion"]] = emotions.get(item["emotion"], 0) + 1
            sentiments[item["sentiment"]] = sentiments.get(item["sentiment"], 0) + 1

        dominant_emotion = max(emotions, key=emotions.get)
        dominant_sentiment = max(sentiments, key=sentiments.get)
        return {
            "dominant_emotion": dominant_emotion,
            "dominant_sentiment": dominant_sentiment,
        }

    def get_memory_snapshot(self, query=None):
        return {
            "recent_context": self.get_context_text(),
            "relevant_memories": self.get_relevant_memories(query),
            "user_profile": self.get_user_profile_summary(),
            "emotional_summary": self.get_emotional_summary(),
            "reflections": self.reflections[-3:],
        }

    def log_execution(self, actions):
        self.execution_logs.append({
            "timestamp": datetime.now().isoformat(),
            "actions": actions,
        })
        self.execution_logs = self.execution_logs[-self.max_execution_logs :]

    def get_execution_logs(self, limit=10):
        return self.execution_logs[-limit:]

    def clear_memory(self, session_id=None):
        if session_id:
            self.history = [msg for msg in self.history if msg["session"] != session_id]
            self.long_term_memories = [msg for msg in self.long_term_memories if msg["session"] != session_id]
        else:
            self.history = []
            self.long_term_memories = []
            self.user_profile = {
                "preferences": [],
                "behavioral_patterns": [],
                "emotional_history": [],
            }
            self.reflections = []
            self.execution_logs = []
