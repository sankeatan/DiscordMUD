from openai import OpenAI
from logger import setup_logger
import os

logger = setup_logger('ai_npc')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class AINPC:
    def __init__(self, name, personality):
        self.name = name
        self.personality = personality
        self.client = OpenAI(api_key=OPENAI_API_KEY)  # Initialize the OpenAI client

    def build_prompt(self, player_action):
        return [
            {"role": "system", "content": f"You are {self.name}, an NPC with a {self.personality} personality. Respond to the player's action."},
            {"role": "user", "content": f"Player: {player_action}"},
            {"role": "assistant", "content": ""}
        ]

    def generate_dialogue(self, player_action):
        """Generate NPC dialogue dynamically based on player input and NPC personality."""
        prompt = self.build_prompt(player_action)

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if you have access
                messages=prompt,
                max_tokens=150,
                temperature=0.7
            )

            npc_response = response.choices[0].message.content
            return npc_response
        except Exception as e:
            logger.error(f"Error generating dialogue: {str(e)}")
            return "I'm sorry, I'm having trouble understanding right now."
    
    def generate_combat_narrative(self, actions, outcomes):
        """
        Create a cohesive narrative based on actions and their outcomes.
        """
        story = []
        story.append("The battle begins with the following actions:")
        for action in actions:
            story.append(f"{action['player']} chose to {action['action']}.")

        story.append("\nResults of the round:")
        for outcome in outcomes:
            story.append(outcome)

        # Add environmental or enemy-based flavor
        story.append("The enemies seem to regroup for another assault.")
        return "\n".join(story)
    
    def evaluate_creative_action(self, action_prompt):
        """
        Use AI to evaluate the outcome of a creative action.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a GameMaster AI."},
                          {"role": "user", "content": action_prompt}],
                max_tokens=150,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating creative action response: {str(e)}")
            return "The outcome of this action is unclear. Try again!"

# Example Usage
#if __name__ == "__main__":
    #npc = AINPC(name="Blacksmith", personality="friendly")
    #player_action = "Can you repair my sword?"
    #response = npc.generate_dialogue(player_action)
    #print(response)  # NPC dynamically responds using AI
