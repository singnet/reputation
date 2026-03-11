# reputation_runner.py

from datetime import datetime
from reputation_math import *
import pandas as pd
import pickle
from typing import Dict, Optional
from pathlib import Path
import math

REQUIRED_COLUMNS = ["from", "to", "value", "timestamp", "transactionID"]

OPTIONAL_COLUMNS = [ "weight", "normalized_value", "transaction_type"]
DEFAULT_PROGRESS_SUBDIR = "reputation_progress"
def _date_str(d) -> str:
    # d can be datetime.date or datetime
    if isinstance(d, datetime):
        d = d.date()
    return str(d)  # YYYY-MM-DD
    
def load_csv(path: str) -> pd.DataFrame:
    """Load a CSV file and validate required columns."""
    df = pd.read_csv(path)
    return normalize_df(df)

def load_json(path: str) -> pd.DataFrame:
    """Load a JSON file and validate required columns."""
    df = pd.read_json(path)
    return normalize_df(df)

def load_parquet(path: str) -> pd.DataFrame:
    """Load a Parquet file and validate required columns."""
    df = pd.read_parquet(path)
    return normalize_df(df)

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize required fields in a DataFrame."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Fill missing optional fields with defaults
    if "weight" not in df.columns:
        df["weight"] = None
    if "normalized_value" not in df.columns:
        df["normalized_value"] = None
    if "transaction_type" not in df.columns:
        df["transaction_type"] = None

    return df

def preprocess_transactions(df: pd.DataFrame, scale: float) -> pd.DataFrame:
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    df = df.sort_values('timestamp')
    df['normalized_value'] = df['value'] / scale
    return df


class ReputationEngine:
    def __init__(self, df, logger, *,start_date,cutoff_date, daily_reputations = None,conservativity=0.9,liquid = True,default_rep=0.5,precision=1.0,
                 scale=10**8,anchor_enabled = False,anchor_address="0x000000000000000000000000000000000000dead",weighting=True,logratings=False,
                 logranks=False,denomination=True,unrated=False,temporal_aggregation=False,predictiveness=0,
                 normalized_ranks=False,need_occurance=True, update_method="exponential" , spendings=0, compute_cap_enabled = False,
                 window=7,fallback_cap=1.0,save_path="reputation_progress.pkl",reputation_weights: Optional[Dict[str, float]] = None,
                multiple_reputations = True):
        """
        Initialize the reputation engine with data and parameters.
        """
        self.df = df
        self.logger = logger
        self.cutoff_date = cutoff_date
        self.start_date = start_date

        # Reputation algorithm parameters
        self.conservativity = conservativity
        self.default_rep = default_rep
        self.precision = precision
        self.scale = scale
        self.anchor_enabled = anchor_enabled
        self.anchor = anchor_address
        self.weighting = weighting
        self.logratings = logratings
        self.logranks = logranks
        self.denomination = denomination
        self.unrated = unrated
        self.temporal_aggregation = temporal_aggregation
        self.predictiveness = predictiveness
        self.normalized_ranks = normalized_ranks
        self.need_occurance = need_occurance
        self.update_method = update_method
        self.spendings = spendings
        self.window = window
        self.compute_cap_enabled = compute_cap_enabled
        self.fallback_cap = fallback_cap
        self.reputation01 = {}
        self.external_updates_by_date = {}
        
        self.daily_main_reputations = {}  # per-day snapshots of reputation01        
        self.save_path = save_path

        # If save_path looks like a file (e.g., endswith .pkl), use its parent
        p = Path(self.save_path)
        base_dir = p.parent if p.suffix else p  # file -> parent, dir -> itself
        self.progress_root = base_dir / DEFAULT_PROGRESS_SUBDIR

        # Internal state
        self.reputation = {}               # Current rep
        self.previous_reputation = {}      # For raters
        self.first_occurance = {}          # When each address was first seen
        if daily_reputations is None:
            self.daily_reputations = {}        # Store per-day reputations
        else:
            self.daily_reputations = daily_reputations
        if reputation_weights is None:
            reputation_weights = {"main": 1.0}
        self.reputation_weights = self.normalize_weights(reputation_weights)
        self._reputation_weights = dict(self.reputation_weights)
        # External reputation state (hold-last-value)
        self.external_rep = {}  # Dict[str, Dict[address, float]]  e.g. {"github": {...}, "telegram": {...}}
        
        # Optional: store external history per day (since you explicitly want this)
        self.daily_external_reps = {}  # Dict[str(date), Dict[str(source), Dict[address, float]]]        

        self.processed_dates = set(self.daily_reputations.keys())
        self.predictive_data = {}
        self.liquid = liquid
        self.multiple_reputations = multiple_reputations
            


    def initialize_anchor(self):
        """
        Ensure the anchor address is present in the reputation state.
        """
        if self.anchor not in self.reputation:
            self.reputation[self.anchor] = 0.0
            self.previous_reputation[self.anchor] = 0.0
            self.first_occurance[self.anchor] = self.start_date.date()

    
    
    
    def set_reputation_weights(self, weights: Dict[str, float]) -> None:
        """
        Input:
            weights = {"main": 0.7, "github": 0.2, "telegram": 0.1}
    
        Output:
            0 on success, error code otherwise
        """
    
        if not isinstance(weights, dict) or not weights:
            raise ValueError("weights must be a non-empty dict[str, float].")
    
        
        for k, v in weights.items():
            if not isinstance(k, str):
                raise ValueError("Weights keys must be a string.")
            if not isinstance(v, (int, float)):
                raise ValueError("Weights values must be float.")
    
        normalized = self.normalize_weights(weights)
        self.reputation_weights = normalized
        self._reputation_weights = dict(normalized)


    def normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Ensures:
          - All weights are strictly > 0
          - Sum > 0
          - Returns normalized weights summing to 1
        """
        total = 0.0
        for k, v in weights.items():
            if not isinstance(v, (int, float)):
                raise ValueError(f"Weight for '{k}' must be numeric.")
            if v <= 0:
                raise ValueError(f"Weight for '{k}' must be strictly positive.")
            total += float(v)
    
        if total <= 0:
            raise ValueError("Sum of weights must be > 0.")
    
        return {k: float(v) / total for k, v in weights.items()}



    
    def get_reputation_weights(self) -> Dict[str, float]:
        return dict(self._reputation_weights)
    
    
    def _step_one_day(self, date, group):
        assert self.reputation01 is not self.reputation
        vals = group["value"].astype(float)
        vmin, vmax = vals.min(), vals.max()
        
        solo_signal = (1.0 + self.default_rep) / 2.0
        delta = 0.0005  # "small tx still positive"
        min_signal = min(1.0, self.default_rep + delta)
        
        if vmax == vmin:
            norm_vals = pd.Series(solo_signal, index=group.index)
        else:
            scaled01 = (vals - vmin) / (vmax - vmin)  # 0..1
            norm_vals = min_signal + (1.0 - min_signal) * scaled01  # [min_signal, 1]

        
        # 1. Compute cap if enabled
        if self.compute_cap_enabled:
            cap = compute_cap(self.df, date, window=self.window, scale=self.scale, fallback=self.fallback_cap)
        else:
            cap = None

        # 2. Prepare daily transactions
        cap_val = cap if cap is not None else float("inf")
        daily_tx = [
            {
                'from': row['from'],
                'to': row['to'],
                'value': float(norm_vals.loc[idx]),  # in (eps, 1]
                'weight': None,
                'time': datetime.combine(date, datetime.min.time())
            }
            for idx, row in group.iterrows()
        ]
        # 3. Add anchor transaction
        if self.anchor_enabled:
            daily_tx.append({'from': self.anchor,'to': self.anchor,'value': 1.0,'weight': None,
                 'time': datetime.combine(date, datetime.min.time())})

            # 4. Ensure anchor is initialized
            self.initialize_anchor()

        # 5. Prepare raw contribution array
        array1, dates_array, to_array, _ = reputation_calc_p1(
            daily_tx,
            conservatism=self.conservativity,
            precision=self.precision,
            temporal_aggregation=self.temporal_aggregation,
            need_occurance=self.need_occurance,
            logratings=self.logratings,
            downrating=False,
            weighting=self.weighting,
            rater_bias=None,
            averages=None)

        # 6. Update reputations if new addresses appeared
        if self.multiple_reputations:
            self.reputation01 = update_reputation(
            self.reputation01, array1,default_reputation=self.default_rep,spendings=0)
            
        self.reputation = update_reputation(self.reputation,array1,default_reputation=self.default_rep,spendings=0)

        # 7. Compute differential
        ### Note this differential is just F(τ,i,j,k) * R_g(t-1,j) * W(τ,i,j,k) , for now. We still need to multiply by H_k and divide by:
        ### SUM_{k,j, if  t-1=<τ<t}( WeH_d(k) *  R_g(t-1,j) * W(τ,i,j,k)  )
            
        new_reputation, self.previous_reputation = calculate_new_reputation(
            logging=self.logger,new_array=array1,to_array=to_array,
            reputation=self.reputation,rating=True,precision=self.precision,
            previous_rep=self.previous_reputation,default=self.default_rep,
            unrated=self.unrated,normalizedRanks=self.normalized_ranks,
            weighting=self.weighting,
            denomination=self.denomination,
            liquid=self.liquid,
            logratings=self.logratings,
            logranks=self.logranks,
            predictiveness=self.predictiveness,
            predictive_data=self.predictive_data            
        )


        

#        # 8. Normalize the output
#        new_reputation = normalized_differential(
#            new_reputation,
#            normalizedRanks=self.normalized_ranks,
#            our_default=self.default_rep,
#            spendings=0,
#            log=False
#        )

        # 9. Blend into final reputation using chosen update method
        ### CURRENTLY NOT WORKING YET (ELSE IS WORKING).
        if self.multiple_reputations:
            if self.update_method == "time_weighted":
                self.reputation01 = update_reputation_time_weighted(
                    self.reputation,new_reputation,t0=self.start_date,
                    t_prev=datetime.combine(date, datetime.min.time()) - timedelta(days=1),
                    t_now=datetime.combine(date, datetime.min.time()),
                    default_rep=self.default_rep)
            else:
                #print("reputation01 before:",self.reputation01)
                self.reputation01 = update_reputation_approach_d(
                    self.first_occurance,self.reputation,new_reputation,
                    since=datetime.combine(date, datetime.min.time()) - timedelta(days=1),
                    our_date=datetime.combine(date, datetime.min.time()),
                    default_rep=self.default_rep,
                    conservativity=self.conservativity,
                    old_reputation_unrated=self.reputation01)
            ### Now we have to sum up reputation01 with external reputations:
            # Compose final reputation (main + externals)
            #print("reputation01 afeter:",self.reputation01)
            self.reputation = self.compose_reputation()
        

        else:
            if self.update_method == "time_weighted":
                self.reputation = update_reputation_time_weighted(
                    self.reputation,new_reputation,t0=self.start_date,
                    t_prev=datetime.combine(date, datetime.min.time()) - timedelta(days=1),
                    t_now=datetime.combine(date, datetime.min.time()),
                    default_rep=self.default_rep)
            else:
                self.reputation = update_reputation_approach_d(
                    self.first_occurance,self.reputation,new_reputation,
                    since=datetime.combine(date, datetime.min.time()) - timedelta(days=1),
                    our_date=datetime.combine(date, datetime.min.time()),
                    default_rep=self.default_rep,
                    conservativity=self.conservativity)            
        self.daily_external_reps[str(date)] = {src: rep.copy() for src, rep in self.external_rep.items()}

        self.logger.info(f"Updated reputation for {date}, {len(self.reputation)} addresses")
        # store main-only stream. This is the reputation01, so the first one, that is technically not external
        
        self.daily_main_reputations[str(date)] = self.reputation01.copy()
        self.daily_reputations[str(date)] = self.reputation.copy()
        # store external streams (if implemented)


    def prepare_simulation_environment(self):
        """
        Prepare normalized data, set start date, cutoff, and initial cap if not provided.
        Should be called after df is loaded and before running the simulation.
        """
        # 1. Ensure timestamp is datetime
        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"]).dt.tz_localize(None)
        self.df = self.df.sort_values("timestamp")
    
        # 2. Add normalized_value if not present
        if "normalized_value" not in self.df.columns:
            self.df["normalized_value"] = self.df["value"] / self.scale
    
        # 3. Set start date if not set
        if not hasattr(self, 'start_date') or self.start_date is None:
            self.start_date = self.df["timestamp"].min().normalize()
    
        # 4. Set cutoff if not set
        if not hasattr(self, 'cutoff_date') or self.cutoff_date is None:
            self.cutoff_date = self.df["timestamp"].max().normalize()
    
        # 5. Calculate initial cap if not already set
        cap_start = self.start_date + timedelta(days=7)
        initial_window = self.df[self.df["timestamp"] < cap_start].copy()
    
        if not hasattr(self, 'fallback_cap') or self.fallback_cap is None:
            self.fallback_cap = np.percentile(initial_window["normalized_value"], 95)
    
        self.logger.info(f"Start date: {self.start_date}")
        self.logger.info(f"Cutoff date: {self.cutoff_date}")
        self.logger.info(f"Initial 95th percentile cap: {self.fallback_cap:.4f}")

    def determine_start_date(self):
        """
        Determine the simulation start date:
        - If some dates are already processed, pick the next day after the latest one.
        - Otherwise, use self.start_date (defined during setup).
        """
        if self.daily_reputations:
            last_date_str = max(self.daily_reputations.keys())
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            return last_date + timedelta(days=1)
        return self.start_date.date()

    def _ensure_external_coverage(self, all_addrs, *, default_external=None) -> None:
        """
        Guarantee that for every external source mentioned in self.reputation_weights,
        every address in all_addrs has a stored external value.
        """
        if default_external is None:
            default_external = self.default_rep
    
        for src_name in self.reputation_weights.keys():
            if src_name == "main":
                continue
            if src_name not in self.external_rep:
                self.external_rep[src_name] = {}
            for a in all_addrs:
                self.external_rep[src_name].setdefault(a, default_external)   

    def compose_reputation(self) -> Dict[str, float]:
        """
        Compose main (self.reputation01) with external_rep using self.reputation_weights.
        Returns a fresh dict.
        """
        weights = self.reputation_weights
        main = self.reputation01 if self.multiple_reputations else self.reputation
    
        # union addresses across main + all external states
        all_addrs = set(main.keys())
        for src_map in self.external_rep.values():
            all_addrs |= set(src_map.keys())
    
        # ensure complete coverage so lookups never "drop to 0" accidentally
        self._ensure_external_coverage(all_addrs, default_external=self.default_rep)
    
        out = {}
        for a in all_addrs:
            r = weights.get("main", 0.0) * float(main.get(a, self.default_rep))
            for src_name, src_map in self.external_rep.items():
                w = weights.get(src_name, 0.0)
                if w == 0.0:
                    continue
                r += w * float(src_map.get(a, self.default_rep))
    
            # clamp [0,1]
            if r < 0.0: 
                self.logger.warning(f"Composed rep <0 for {a}: {r}. Clamping to 0.")
                r = 0.0
            elif r > 1.0:
                self.logger.warning(f"Composed rep >1 for {a}: {r}. Clamping to 1.")
                r = 1.0
            out[a] = r
    
        return out


    def ingest_external_updates(self, source: str, updates: Dict[str, float]) -> None:
        if source not in self.external_rep:
            self.external_rep[source] = {}
    
        for addr, val in updates.items():
            # try coerce
            try:
                v = float(val)
            except Exception:
                # no usable value: keep old if exists, else default
                if addr not in self.external_rep[source]:
                    self.external_rep[source][addr] = self.default_rep
                continue
    
            # reject non-finite
            if not math.isfinite(v):
                if addr not in self.external_rep[source]:
                    self.external_rep[source][addr] = self.default_rep
                continue
    
            # optional clamp if externals are [0,1]
            v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
    
            self.external_rep[source][addr] = v
    
    def run_reputation(self):
        start_date = self.determine_start_date()
    
        df_sorted = self.df.sort_values("timestamp").copy()
        df_sorted["date"] = df_sorted["timestamp"].dt.date
    
        for date, group in df_sorted.groupby("date", sort=True):
            if date < start_date:
                continue
            if date > self.cutoff_date.date():
                break
            # 0) Ingest external updates for this date (sparse; hold-last-value)
            ### This is also a placeholder for actual updates, when incorporated
            ### PROBLEM (above)
            updates_for_day = self.external_updates_by_date.get(str(date), {})
            for source, updates in updates_for_day.items():
                self.ingest_external_updates(source, updates)
            self._step_one_day(date, group)
            self.save_progress_day(date)


        
    def save_progress_single_file(self):
        payload = {
            # histories
            "daily_reputations": self.daily_reputations,                 # composed
            "daily_main_reputations": self.daily_main_reputations,       # main-only (reputation01 history)
            "daily_external_reps": getattr(self, "daily_external_reps", {}),
    
            # current states (for fast resume)
            "main_rep_state": getattr(self, "reputation01", {}),
            "composed_rep_state": getattr(self, "reputation", {}),
            "external_rep_state": getattr(self, "external_rep", {}),
    
            # policy/config
            "reputation_weights": self.reputation_weights,
            "params": {
                "conservativity": self.conservativity,
                "default_rep": self.default_rep,
                "precision": self.precision,
                "scale": self.scale,
                "weighting": self.weighting,
                "denomination": self.denomination,
                "liquid": self.liquid,
                "logratings": self.logratings,
                "logranks": self.logranks,
                "compute_cap_enabled": self.compute_cap_enabled,
                "window": self.window,
                "fallback_cap": self.fallback_cap,
                "multiple_reputations": self.multiple_reputations,
                "update_method": self.update_method,
                "anchor_enabled": self.anchor_enabled,
                "anchor": self.anchor,
            },
        }
        with open(self.save_path, "wb") as f:
            pickle.dump(payload, f)
        self.logger.info(f"Saved progress to {self.save_path}")

    
    def load_progress_single_file(self, path=None, *, load_settings=True):
        load_path = path or self.save_path
    
        with open(load_path, "rb") as f:
            obj = pickle.load(f)
    
        # ---- New format (payload dict) ----
        if isinstance(obj, dict) and "daily_reputations" in obj:
            # histories
            self.daily_reputations = obj.get("daily_reputations", {}) or {}
            self.daily_main_reputations = obj.get("daily_main_reputations", {}) or {}
            self.daily_external_reps = obj.get("daily_external_reps", {}) or {}
    
            # current external state (hold-last-value)
            self.external_rep = obj.get("external_rep_state", {}) or {}
    
            # weights
            saved_weights = obj.get("reputation_weights", None)
            if isinstance(saved_weights, dict) and saved_weights:
                self.reputation_weights = self.normalize_weights(saved_weights)
                self._reputation_weights = dict(self.reputation_weights)
    
            # settings
            if load_settings:
                params = obj.get("params", {}) or {}
                # only apply keys that exist to avoid surprises
                for k, v in params.items():
                    if hasattr(self, k):
                        setattr(self, k, v)
    
            # restore current main/composed states from latest day if possible
            if self.daily_main_reputations:
                last_day_main = max(self.daily_main_reputations.keys())
                self.reputation01 = dict(self.daily_main_reputations[last_day_main])
            else:
                self.reputation01 = dict(obj.get("main_rep_state", {})) if self.multiple_reputations else {}
    
            if self.daily_reputations:
                last_day = max(self.daily_reputations.keys())
                self.reputation = dict(self.daily_reputations[last_day])
            else:
                self.reputation = dict(obj.get("composed_rep_state", {}))
    
            # processed_dates used for resuming
            self.processed_dates = set(self.daily_reputations.keys())
    
            self.logger.info(
                f"Loaded progress from {load_path}. "
                f"Days composed: {len(self.daily_reputations)}, "
                f"Days main: {len(self.daily_main_reputations)}, "
                f"Days external: {len(self.daily_external_reps)}"
            )
            return
    
        # ---- Old format (legacy: daily_reputations only) ----
        if isinstance(obj, dict):
            self.daily_reputations = obj
            self.daily_main_reputations = {}
            self.daily_external_reps = {}
            self.external_rep = {}
    
            if self.daily_reputations:
                last_day = max(self.daily_reputations.keys())
                self.reputation = dict(self.daily_reputations[last_day])
            else:
                self.reputation = {}
    
            if getattr(self, "multiple_reputations", False):
                self.reputation01 = dict(self.reputation)
    
            self.processed_dates = set(self.daily_reputations.keys())
    
            self.logger.info(f"Loaded legacy progress from {load_path}. Days: {len(self.daily_reputations)}")
            return
    
        raise ValueError(f"Unrecognized progress format in {load_path}")

    
    def _progress_paths(self, root=None):
        root_dir = Path(root) if root is not None else self.progress_root
        settings_path = root_dir / "settings.pkl"
        days_dir = root_dir / "days"
        return root_dir, settings_path, days_dir

    def save_settings(self, root=None):
        """
        Saves settings/weights needed to reproduce the run.
        Safe to overwrite every time (small file).
        """
        root_dir, settings_path, days_dir = self._progress_paths(root)
        root_dir.mkdir(parents=True, exist_ok=True)
        days_dir.mkdir(parents=True, exist_ok=True)

        settings = {
            "reputation_weights": self.reputation_weights,
            "params": {
                "conservativity": self.conservativity,
                "default_rep": self.default_rep,
                "precision": self.precision,
                "scale": self.scale,
                "weighting": self.weighting,
                "denomination": self.denomination,
                "liquid": self.liquid,
                "logratings": self.logratings,
                "logranks": self.logranks,
                "compute_cap_enabled": self.compute_cap_enabled,
                "window": self.window,
                "fallback_cap": self.fallback_cap,
                "multiple_reputations": self.multiple_reputations,
                "update_method": self.update_method,
                "anchor_enabled": self.anchor_enabled,
                "anchor": self.anchor,
            },
        }

        with open(settings_path, "wb") as f:
            pickle.dump(settings, f)

        self.logger.info(f"Saved settings to {settings_path}")

    def save_progress_day(self, day, root=None):
        """
        One file per day. Stores only daily snapshots + current states needed to resume.
        """
        root_dir, settings_path, days_dir = self._progress_paths(root)
        root_dir.mkdir(parents=True, exist_ok=True)
        days_dir.mkdir(parents=True, exist_ok=True)

        day_s = _date_str(day)
        day_path = days_dir / f"{day_s}.pkl"

        # Always keep settings up to date (tiny, cheap)
        self.save_settings(root=root)

        payload = {
            "date": day_s,

            # daily snapshots (these are the “history”)
            "composed_day": self.daily_reputations.get(day_s, {}),
            "main_day": getattr(self, "daily_main_reputations", {}).get(day_s, {}),
            "external_day": getattr(self, "daily_external_reps", {}).get(day_s, {}),

            # current states (for fast resume)
            "composed_rep_state": dict(self.reputation),
            "main_rep_state": dict(getattr(self, "reputation01", {})),
            "external_rep_state": dict(getattr(self, "external_rep", {})),
        }

        with open(day_path, "wb") as f:
            pickle.dump(payload, f)

        self.logger.info(f"Saved day {day_s} to {day_path}")

    def load_progress_dir(self, root=None, *, load_settings=True, up_to_day=None):
        """
        Loads settings.pkl (optional) and then replays day files up to a target day.
        Rebuilds daily_reputations / daily_main_reputations / daily_external_reps and restores current states.
        """
        root_dir, settings_path, days_dir = self._progress_paths(root)

        if load_settings and settings_path.exists():
            with open(settings_path, "rb") as f:
                settings = pickle.load(f)

            saved_weights = settings.get("reputation_weights", None)
            if isinstance(saved_weights, dict) and saved_weights:
                self.reputation_weights = self.normalize_weights(saved_weights)
                self._reputation_weights = dict(self.reputation_weights)

            params = settings.get("params", {}) or {}
            for k, v in params.items():
                if hasattr(self, k):
                    setattr(self, k, v)

            self.logger.info(f"Loaded settings from {settings_path}")

        # enumerate day files
        if not days_dir.exists():
            raise FileNotFoundError(f"No days directory found at {days_dir}")

        day_files = sorted(days_dir.glob("*.pkl"))
        if not day_files:
            raise FileNotFoundError(f"No day files found in {days_dir}")

        # filter up_to_day
        if up_to_day is not None:
            day_files = [p for p in day_files if p.stem <= up_to_day]
            if not day_files:
                raise FileNotFoundError(f"No day files <= {up_to_day} found in {days_dir}")

        # reset histories
        self.daily_reputations = {}
        self.daily_main_reputations = {}
        self.daily_external_reps = {}

        last_payload = None
        for p in day_files:
            with open(p, "rb") as f:
                payload = pickle.load(f)
            d = payload["date"]

            self.daily_reputations[d] = payload.get("composed_day", {}) or {}
            self.daily_main_reputations[d] = payload.get("main_day", {}) or {}
            self.daily_external_reps[d] = payload.get("external_day", {}) or {}

            last_payload = payload

        # restore current states from last loaded day
        if last_payload is not None:
            self.reputation = last_payload.get("composed_rep_state", {}) or {}
            self.reputation01 = last_payload.get("main_rep_state", {}) or {}
            self.external_rep = last_payload.get("external_rep_state", {}) or {}
            self.processed_dates = set(self.daily_reputations.keys())

            self.logger.info(
                f"Loaded {len(self.daily_reputations)} days from {days_dir}. "
                f"Last day: {max(self.daily_reputations.keys())}"
            )