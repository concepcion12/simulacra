"""
Core Agent class implementing the layered behavioral architecture.
"""
import uuid
from typing import Dict, List, Optional
from collections import deque
import numpy as np

from simulacra.utils.types import (
    AgentID, PlotID, ActionType, BehaviorType, SubstanceType,
    PersonalityTraits, InternalState, AddictionState, GamblingContext,
    ActionBudget, EnvironmentalCue, ActionOutcome, CueType,
    EmploymentInfo, HousingInfo
)
from .behavioral_economics import (
    ProspectTheoryModule, TemporalDiscountingModule, DualProcessModule,
    GamblingBiasModule, HabitFormationModule, AddictionModule
)
from .decision_making import DecisionMaker, Action, ActionContext
from .action_outcomes import ActionOutcomeGenerator, StateUpdater, OutcomeContext


class Agent:
    """
    Psychologically realistic agent with behavioral economics-based decision making.
    """

    def __init__(
        self,
        agent_id: Optional[AgentID] = None,
        name: Optional[str] = None,
        personality: Optional[PersonalityTraits] = None,
        initial_wealth: float = 1000.0,
        initial_location: Optional[PlotID] = None
    ):
        """
        Initialize an agent with personality and initial conditions.

        Args:
            agent_id: Unique identifier (generated if not provided)
            name: Agent name (generated if not provided)
            personality: Personality traits (randomized if not provided)
            initial_wealth: Starting wealth
            initial_location: Starting location in the city
        """
        # Identity
        self.id = agent_id or AgentID(str(uuid.uuid4()))
        self.name = name or f"Agent_{self.id[:8]}"

        # Location and housing
        self.current_location = initial_location
        self.home: Optional[HousingInfo] = None  # Will be set when agent finds housing
        self.employment: Optional[EmploymentInfo] = None  # Will be set when agent finds job

        # Personality (static traits)
        self.personality = personality or self._generate_random_personality()

        # Dynamic internal state
        self.internal_state = InternalState(
            wealth=initial_wealth,
            monthly_expenses=800.0  # Base living expenses
        )

        # Behavioral states
        self.habit_stocks = {
            BehaviorType.DRINKING: 0.0,
            BehaviorType.GAMBLING: 0.0
        }

        self.addiction_states = {
            SubstanceType.ALCOHOL: AddictionState()
        }

        self.craving_intensities = {
            SubstanceType.ALCOHOL: 0.0,
            BehaviorType.GAMBLING: 0.0
        }

        # Context and memory
        self.gambling_context = GamblingContext()

        # Action management
        self.action_budget = ActionBudget()
        self.action_history = deque(maxlen=100)  # Keep last 100 actions

        # Behavioral modules
        self.prospect_theory = ProspectTheoryModule()
        self.temporal_discounting = TemporalDiscountingModule()
        self.dual_process = DualProcessModule()
        self.gambling_bias = GamblingBiasModule()
        self.habit_formation = HabitFormationModule()
        self.addiction_module = AddictionModule()

        # Decision making
        self.decision_maker = DecisionMaker()

        # Action outcome system
        self.outcome_generator = ActionOutcomeGenerator()
        self.state_updater = StateUpdater()

    def _generate_random_personality(self) -> PersonalityTraits:
        """Generate random but realistic personality traits."""
        return PersonalityTraits(
            baseline_impulsivity=np.clip(np.random.normal(0.5, 0.2), 0, 1),
            risk_preference_alpha=np.clip(np.random.normal(0.88, 0.1), 0.5, 1.0),
            risk_preference_beta=np.clip(np.random.normal(0.88, 0.1), 0.5, 1.0),
            risk_preference_lambda=np.clip(np.random.normal(2.25, 0.5), 1.0, 4.0),
            cognitive_type=np.clip(np.random.normal(0.6, 0.2), 0, 1),
            addiction_vulnerability=np.clip(np.random.normal(0.3, 0.2), 0, 1),
            gambling_bias_strength=np.clip(np.random.normal(0.4, 0.2), 0, 1)
        )

    @classmethod
    def create_random(cls) -> 'Agent':
        """Factory method to create agent with random characteristics."""
        return cls()

    @classmethod
    def create_with_profile(
        cls,
        profile_type: str,
        **kwargs
    ) -> 'Agent':
        """
        Create agent with predefined personality profile.

        Args:
            profile_type: One of 'impulsive', 'cautious', 'balanced', 'vulnerable'
            **kwargs: Additional parameters

        Returns:
            Agent with specified profile
        """
        profiles = {
            'impulsive': PersonalityTraits(
                baseline_impulsivity=0.8,
                risk_preference_alpha=0.7,
                risk_preference_beta=0.7,
                risk_preference_lambda=1.5,
                cognitive_type=0.3,
                addiction_vulnerability=0.6,
                gambling_bias_strength=0.7
            ),
            'cautious': PersonalityTraits(
                baseline_impulsivity=0.2,
                risk_preference_alpha=0.95,
                risk_preference_beta=0.95,
                risk_preference_lambda=3.0,
                cognitive_type=0.8,
                addiction_vulnerability=0.1,
                gambling_bias_strength=0.2
            ),
            'balanced': PersonalityTraits(
                baseline_impulsivity=0.5,
                risk_preference_alpha=0.88,
                risk_preference_beta=0.88,
                risk_preference_lambda=2.25,
                cognitive_type=0.6,
                addiction_vulnerability=0.3,
                gambling_bias_strength=0.4
            ),
            'vulnerable': PersonalityTraits(
                baseline_impulsivity=0.7,
                risk_preference_alpha=0.6,
                risk_preference_beta=0.8,
                risk_preference_lambda=1.8,
                cognitive_type=0.4,
                addiction_vulnerability=0.8,
                gambling_bias_strength=0.6
            )
        }

        personality = profiles.get(profile_type, profiles['balanced'])
        return cls(personality=personality, **kwargs)

    def update_internal_states(self, delta_time: int = 1) -> None:
        """
        Update all internal states for time progression.

        Args:
            delta_time: Time passed in months
        """
        # Update addiction states
        self._update_addiction_states(delta_time)

        # Update habit stocks
        self._update_habit_stocks(delta_time)

        # Update cravings
        self._update_cravings()

        # Natural state progression
        self._update_mood_and_stress(delta_time)

        # Restore self-control
        self._restore_self_control(delta_time)

    def _update_addiction_states(self, delta_time: int) -> None:
        """Update addiction mechanics."""
        alcohol_state = self.addiction_states[SubstanceType.ALCOHOL]

        # Tolerance decay
        alcohol_state.tolerance_level *= 0.95 ** delta_time

        # Update withdrawal
        if alcohol_state.time_since_last_use > 0:
            alcohol_state.withdrawal_severity = self.addiction_module.calculate_withdrawal_severity(
                alcohol_state.stock,
                alcohol_state.time_since_last_use
            )

            # Addiction stock decay
            alcohol_state.stock = self.addiction_module.update_addiction_stock(
                alcohol_state.stock,
                consumption=0,  # No consumption this period
                decay_rate=0.93
            )

        alcohol_state.time_since_last_use += delta_time

    def _update_habit_stocks(self, delta_time: int) -> None:
        """Update habit formation."""
        # Habits decay slowly without reinforcement
        decay_factor = 0.95 ** delta_time

        for behavior in self.habit_stocks:
            self.habit_stocks[behavior] *= decay_factor

    def _update_cravings(self) -> None:
        """Update craving intensities based on current state."""
        # Alcohol craving from addiction/withdrawal
        alcohol_state = self.addiction_states[SubstanceType.ALCOHOL]
        base_craving = (
            alcohol_state.withdrawal_severity * 0.5 +
            alcohol_state.stock * 0.1
        )

        # Stress amplifies craving
        if self.internal_state.stress > 0.7:
            base_craving *= 1.3

        self.craving_intensities[SubstanceType.ALCOHOL] = min(1.0, base_craving)

        # Gambling craving from habit and financial pressure
        gambling_craving = self.habit_stocks[BehaviorType.GAMBLING] * 0.2

        if self.internal_state.wealth < self.internal_state.monthly_expenses:
            gambling_craving *= 1.5  # Financial pressure increases gambling urge

        self.craving_intensities[BehaviorType.GAMBLING] = min(1.0, gambling_craving)

    def _update_mood_and_stress(self, delta_time: int) -> None:
        """Natural mood and stress progression."""
        # Mood regresses toward neutral
        self.internal_state.mood *= 0.9 ** delta_time

        # Stress has natural decay but with a floor based on life circumstances
        base_stress = 0.1  # Minimum stress level

        # Financial stress
        if self.internal_state.wealth < self.internal_state.monthly_expenses * 0.5:
            base_stress += 0.2

        # Unemployment stress
        if self.employment is None:
            base_stress += 0.15

        # Housing stress
        if self.home is None:
            base_stress += 0.25

        # Decay toward base stress
        stress_diff = self.internal_state.stress - base_stress
        self.internal_state.stress = base_stress + stress_diff * (0.8 ** delta_time)

        # Ensure bounds
        self.internal_state.mood = np.clip(self.internal_state.mood, -1, 1)
        self.internal_state.stress = np.clip(self.internal_state.stress, 0, 1)

    def _restore_self_control(self, delta_time: int) -> None:
        """Restore self-control resources over time."""
        restoration_rate = 0.1 * delta_time

        # Better restoration when housed and employed
        if self.home is not None:
            restoration_rate *= 1.2
        if self.employment is not None:
            restoration_rate *= 1.1

        self.internal_state.self_control_resource = min(
            1.0,
            self.internal_state.self_control_resource + restoration_rate
        )

    def process_environmental_cues(self, cues: List[EnvironmentalCue]) -> None:
        """
        Process environmental cues and update internal state.

        Args:
            cues: List of environmental cues to process
        """
        for cue in cues:
            if cue.cue_type == CueType.ALCOHOL_CUE:
                # Amplify alcohol craving
                if self.addiction_states[SubstanceType.ALCOHOL].stock > 0:
                    self.craving_intensities[SubstanceType.ALCOHOL] *= (
                        1 + cue.intensity * 0.3
                    )

            elif cue.cue_type == CueType.GAMBLING_CUE:
                # Trigger gambling memories
                if self.habit_stocks[BehaviorType.GAMBLING] > 0:
                    self.craving_intensities[BehaviorType.GAMBLING] *= (
                        1 + cue.intensity * 0.4
                    )

            elif cue.cue_type == CueType.FINANCIAL_STRESS_CUE:
                # Increase stress
                self.internal_state.stress += cue.intensity * 0.2
                self.internal_state.stress = min(1.0, self.internal_state.stress)

    def get_max_craving(self) -> float:
        """Get maximum craving intensity across all types."""
        all_cravings = list(self.craving_intensities.values())
        return max(all_cravings) if all_cravings else 0.0

    def make_decision(self, available_actions: List[Action], context: Optional[ActionContext] = None) -> Action:
        """
        Make a decision about which action to take.

        Args:
            available_actions: List of possible actions
            context: Optional context information

        Returns:
            Selected action
        """
        if context is None:
            context = ActionContext(agent=self)

        return self.decision_maker.choose_action(self, available_actions, context)

    def can_afford_action(self, action_type: ActionType, time_cost: float) -> bool:
        """
        Check if agent can afford an action.

        Args:
            action_type: Type of action
            time_cost: Time cost in hours

        Returns:
            Whether agent can afford the action
        """
        # Check time budget
        if not self.action_budget.can_afford(time_cost):
            return False

        # Check specific requirements
        if action_type == ActionType.WORK and self.employment is None:
            return False

        if action_type in [ActionType.REST, ActionType.DRINK] and self.home is None:
            # Can only rest/drink at home if homeless
            return False

        return True

    def record_action(self, action: 'Action', outcome: ActionOutcome) -> None:
        """
        Record an executed action in history.

        Args:
            action: Executed action
            outcome: Outcome of the action
        """
        # Apply outcome to agent state
        self.state_updater.apply_outcome(self, outcome)

        # Record action in history
        self.action_history.append((action, outcome))

        # Spend time budget
        self.action_budget.spend(action.time_cost)

    def execute_action(
        self,
        action: Action,
        context: Optional[ActionContext | OutcomeContext] = None,
    ) -> ActionOutcome:
        """
        Execute an action and apply its outcome to agent state.

        Args:
            action: Action to execute
            context: Environmental context for outcome generation (ActionContext or OutcomeContext)

        Returns:
            Generated outcome
        """
        # Handle movement if action has a target location
        if action.target and action.target != self.current_location:
            self._move_to_location(action.target)

        # Convert ActionContext to OutcomeContext if needed
        outcome_context = None
        if context is not None:
            if isinstance(context, OutcomeContext):
                outcome_context = context
            elif isinstance(context, ActionContext):
                # Convert ActionContext to OutcomeContext
                district_wealth = 0.5
                location_quality = 0.5
                social_density = 0.5
                market_conditions = 0.5

                # Extract location-based information if available
                if self.current_location and context.environment:
                    try:
                        plot = context.environment.get_plot(self.current_location)
                        if plot:
                            district = context.environment.get_district(plot.district_id)
                            if district:
                                district_wealth = district.wealth_level
                    except Exception:  # pragma: no cover - fallback
                        pass  # Use defaults if extraction fails

                    # Get market conditions from economy if available
                    try:
                        if hasattr(context.environment, 'global_economy'):
                            market_conditions = context.environment.global_economy.get_job_market_conditions()
                    except Exception:  # pragma: no cover - fallback
                        pass  # Use defaults if extraction fails

                outcome_context = OutcomeContext(
                    environment=context.environment,
                    district_wealth=district_wealth,
                    location_quality=location_quality,
                    market_conditions=market_conditions,
                    social_density=social_density
                )

        # Generate outcome
        outcome = self.outcome_generator.generate_outcome(self, action, outcome_context)

        # Record and apply outcome
        self.record_action(action, outcome)

        return outcome

    def _move_to_location(self, target_location: PlotID) -> None:
        """
        Move agent to a new location.

        Args:
            target_location: Target plot ID to move to
        """
        self.current_location = target_location

        # Update home location if moving home
        if self.home and target_location == self.home.plot_id:
            # Agent is now at home
            pass  # Could trigger home-specific events here

    def get_important_locations(self) -> Dict[str, PlotID]:
        """
        Get dictionary of important locations for this agent.

        Returns:
            Dict mapping location names to plot IDs
        """
        locations = {}

        if self.home:
            locations['home'] = self.home.plot_id

        return locations
