# -*- coding: utf-8 -*-
"""
The code is based on UseCase, User and Appliance classes.
A UseCase instance consists of a list of User instances which own Appliance instances
Within the Appliance class, some other functions are created to define windows of use and,
if needed, specific duty cycles
"""
import numpy as np
import random
import math
import datetime


from typing import List, Union, Iterable


def single_appliance_daily_load_profile(args):
    app, args = args
    app.generate_load_profile(*args, power=app.power[args[0]])

    return args[0], app.daily_use


def get_day_type(day):
    """Given a datetime object return 0 for weekdays or 1 for weekends"""

    if isinstance(day, str):
        day = datetime.date.fromisoformat(day)

    if day.weekday() > 4:
        answer = 1
    else:
        answer = 0
    return answer


def within_peak_time_window(win_start, win_stop, peak_win_start, peak_win_stop):
    """Given determines if a switch on window falls within the peak time window"""
    answer = True
    # start and stop of the given window are both below the lower limit of peak time window
    if win_start < peak_win_start and win_stop < peak_win_start:
        answer = False
    # start and stop of the given window are both above the upper limit of peak time window
    if win_start > peak_win_stop and win_stop > peak_win_stop:
        answer = False
    return answer


def switch_on_parameters():
    """
    Calibration parameters. These can be changed in case the user has some real data against which the model can be calibrated
    They regulate the probability of coincident switch-on within the peak window

    mu_peak corresponds to \mu_{%} in [1], p.8
    s_peak corresponds to \sigma_{%} in [1], p.8

    Notes
    -----
    [1] F. Lombardi, S. Balderrama, S. Quoilin, E. Colombo,
        Generating high-resolution multi-energy load profiles for remote areas with an open-source stochastic model,
        Energy, 2019, https://doi.org/10.1016/j.energy.2019.04.097.
    """

    mu_peak = 0.5  # median value of gaussian distribution [0,1] by which the number of coincident switch_ons is randomly selected
    s_peak = 0.5  # standard deviation (as percentage of the median value) of the gaussian distribution [0,1] above mentioned
    op_factor = 0.5  # off-peak coincidence calculation parameter

    return mu_peak, s_peak, op_factor


def random_variation(var, norm=1):
    """Pick a random variable within a uniform distribution of range [1-var, 1+var]

    Parameters
    ----------
    var: float
        sets the range of the uniform distribution around one
    norm: float
        multiplication factor of the random variable, default = 1

    Returns
    -------
    random number close to norm
    """
    return norm * random.uniform((1 - var), (1 + var))


def duty_cycle(var, t1, p1, t2, p2):
    """Assign a two period duty cycle

    concatenate an array where values equal p1 for a time (t1 +- random variation)
    followed by values equal to p2 for a time (t2 +- random variation)

    Parameters
    ----------
    var: float
        sets the range of the uniform distribution around t1 and t2
    t1: int
        time interval of the first part of the duty cycle in minutes
    p1: float
        power of the first part of the duty cycle in Watt
    t2: int
        time interval of the second part of the duty cycle in minutes
    p2: int
        power of the second part of the duty cycle in Watt

    Returns
    -------
    Power during each timestep of the duty cycle where p1 is repeated (t1 +- random variation) times and p2 is repeated (t2 +- random variation) times.
    The duty cycle is implicitly sampled every minutes (which is the unit for t1 and t2)
    """
    return np.concatenate(
        (
            np.ones(int(random_variation(var=-var, norm=t1))) * p1,
            np.ones(int(random_variation(var=-var, norm=t2))) * p2,
        )
    )


def range_within_window(range_low, range_high, window):
    """Compare a range with a window to see if there is an overlap

    The two cases where there is no overlap between two windows are when the
    range boundaries are both lower than the lowest window value or both
    higher than the highest window value

    """
    return not (
        (range_low < window[0] and range_high < window[0])
        or (range_low > window[1] and range_high > window[1])
    )


def random_choice(var, t1, p1, t2, p2):
    """Chooses one of two duty cycles randomly

    The choice is between a normal duty cycle and a reversed duty cycle (where t1 is swapped with t2 and p1 with p2)

    Parameters
    ----------
    var: float
        sets the range of the uniform distribution around t1 and t2
    t1: int
        time interval of the first part of the duty cycle in minutes
    p1: float
        power of the first part of the duty cycle in Watt
    t2: int
        time interval of the second part of the duty cycle in minutes
    p2: int
        power of the second part of the duty cycle in Watt

    Returns
    -------
    A duty cycle, see function duty_cycle
    """
    return random.choice(
        [
            duty_cycle(var, t1=t1, p1=p1, t2=t2, p2=p2),
            duty_cycle(var, t1=t2, p1=p2, t2=t1, p2=p1),
        ]
    )


def generate_date_range(start_date=None, end_date=None, num_days=1):
    if start_date is not None:
        return [start_date + datetime.timedelta(days=i) for i in range(num_days)]
    elif end_date is not None:
        return [
            end_date - datetime.timedelta(days=num_days - i - 1)
            for i in range(num_days)
        ]
    else:
        today = datetime.datetime.today()
        start_date = datetime(today.year, today.month, today.day)
        return [start_date + datetime.timedelta(days=i) for i in range(num_days)]


def generate_datetime_index(start, end, freq="min"):
    datetime_index = []
    current_time = start
    delta = (
        datetime.timedelta(minutes=1) if freq == "min" else datetime.timedelta(hours=1)
    )  # Modify if needed for other frequencies

    while current_time <= end:
        datetime_index.append(current_time)
        current_time += delta

    return datetime_index


APPLIANCE_ATTRIBUTES = (
    "name",
    "number",
    "power",
    "num_windows",
    "func_time",
    "time_fraction_random_variability",
    "func_cycle",
    "fixed",
    "fixed_cycle",
    "continuous_duty_cycle",
    "occasional_use",
    "flat",
    "thermal_p_var",
    "pref_index",
    "wd_we_type",
    "p_11",
    "t_11",
    "cw11",
    "p_12",
    "t_12",
    "cw12",
    "r_c1",
    "p_21",
    "t_21",
    "cw21",
    "p_22",
    "t_22",
    "cw22",
    "r_c2",
    "p_31",
    "t_31",
    "cw31",
    "p_32",
    "t_32",
    "cw32",
    "r_c3",
    "window_1",
    "window_2",
    "window_3",
    "random_var_w",
)
APPLIANCE_ARGS = (
    "number",
    "power",
    # "p_series",
    "num_windows",
    "func_time",
    "time_fraction_random_variability",
    "func_cycle",
    "fixed",
    "fixed_cycle",
    "continuous_duty_cycle",
    "occasional_use",
    "flat",
    "thermal_p_var",
    "pref_index",
    "wd_we_type",
    "name",
)
WINDOWS_PARAMETERS = ("window_1", "window_2", "window_3", "random_var_w")
DUTY_CYCLE_PARAMETERS = (
    ("p_11", "t_11", "cw11", "p_12", "t_12", "cw12", "r_c1"),
    ("p_21", "t_21", "cw21", "p_22", "t_22", "cw22", "r_c2"),
    ("p_31", "t_31", "cw31", "p_32", "t_32", "cw32", "r_c3"),
)


class UseCase:
    def __init__(
        self,
        name: str = "",
        users: Union[List, None] = None,
        date_start: str = None,
        date_end: str = None,
        parallel_processing: bool = False,
        peak_enlarge: float = 0.15,
        random_seed: int = None,
    ):
        """Creates a UseCase instance for gathering a list of User instances which own Appliance instances

        Parameters
        ----------
        name : str, optional
            name of the usecase instance, by default ""
        users : Union[Iterable,None], optional
            a list of users to be added to the usecase instance, by default None
        date_start: str, optional
            start date of the daily profiles generated by the UseCase instance
        date_end: str, optional
            end date of the daily profiles generated by the UseCase instance
        parallel_processing: bool, optional
            if set True, the profiles will be generated in parallel rather than sequencially
        peak_enlarge: float, optional
            percentage random enlargement or reduction of peak time range length, used in UseCase.calc_peak_time_range
        random_seed: int, optional
            specify seed for the random number generator to exactly reproduce results

        """
        self.name = name
        self._date_start = (
            datetime.datetime.fromisoformat(date_start)
            if isinstance(date_start, str)
            else date_start
        )
        self._date_end = (
            datetime.datetime.fromisoformat(date_end)
            if isinstance(date_end, str)
            else date_end
        )
        self.parallel_processing = parallel_processing
        self._peak_enlarge = peak_enlarge
        self.peak_time_range = None
        self.days = None
        self.__num_days = None
        self.__datetimeindex = None
        self.daily_profiles = None
        self.random_seed = random_seed

        self.appliances = []
        self.users = []
        if users is None:
            users = []
        self.add_user(users)

        self.collect_appliances_from_users()
        if self.date_start is not None and self.date_end is not None:
            self.initialize()

        # Set global random seed if it is specified
        if self.random_seed:
            random.seed(self.random_seed)

    @property
    def date_start(self):
        """Start date of the daily profiles generated by the UseCase instance"""
        return self._date_start

    @date_start.setter
    def date_start(self, new_date):
        self._date_start = (
            datetime.datetime.fromisoformat(new_date)
            if isinstance(new_date, str)
            else new_date
        )

    @property
    def date_end(self):
        """End date of the daily profiles generated by the UseCase instance"""
        return self._date_end

    @date_end.setter
    def date_end(self, new_date):
        self._date_end = (
            datetime.datetime.fromisoformat(new_date)
            if isinstance(new_date, str)
            else new_date
        )

    @property
    def peak_enlarge(self):
        return self._peak_enlarge

    @peak_enlarge.setter
    def peak_enlarge(self, new_peak_enlarge):
        """Percentage random enlargement or reduction of peak time range length, used in UseCase.calc_peak_time_range"""

        if isinstance(new_peak_enlarge, float):
            if new_peak_enlarge >= 0:
                self._peak_enlarge = new_peak_enlarge
                self.peak_time_range = self.calc_peak_time_range()
            else:
                raise ValueError("peak enlarge value must be greater than 0")
        else:
            raise TypeError("peak enlarge must be a float")

    def add_user(self, user) -> None:
        """adds new user to the user property list

        Parameters
        ----------
        user : User
            a user instance

        Raises
        ------
        InvalidType
            any type rather than User will raise the error.
        """
        if isinstance(user, User):
            user.usecase = self
            self.users.append(user)
        elif isinstance(user, list):
            for u in user:
                self.add_user(u)
        else:
            raise TypeError(
                f"{type(user)} is not valid. Only 'User' type is acceptable."
            )

    def collect_appliances_from_users(self):
        """Gather all appliances from a UseCase instance users into self.appliances attribute"""
        appliances = []
        for user in self.users:
            appliances = appliances + user.App_list
        self.appliances = appliances

    @property
    def num_days(self):
        """Number of days for which the UseCase instance will be able to generate profiles"""
        if self.__num_days is None:
            self.initialize()
        return self.__num_days

    @property
    def datetimeindex(self):
        """Return the datetimeindex of the UseCase and call UseCase.initialize() if it was not set"""
        if self.__datetimeindex is None:
            self.initialize()
        return self.__datetimeindex

    def initialize(
        self, num_days: int = None, peak_enlarge: float = None, force: bool = False
    ):
        """Sets the list of days for which to generate profiles and compute peak time range

        Parameters
        ----------
        num_days: int, optional
            if provided it will set the number of days on which profiles will be generated (num_days from date_start
            or num_days until date_end). If both date_start and date_end are provided, num_days will run from date_start
            and a warning will be printed
        peak_enlarge: float, optional
            percentage random enlargement or reduction of peak time range length, used in UseCase.calc_peak_time_range
        force: bool, optional
            if the UseCase instance has already been initialized, it can be forced to take new values with this option set to True

        """
        # TODO allow calendar years multi-year inputs

        if self.is_initialized is True and force is False:
            # logging.warning
            print(
                f"The usecase '{self.name}' is already initialized. If you want to force the reinitialization, use argument `force=True`\n"
                f"You will typically see this message if you provide 'date_start' and 'date_end' to a UseCase instance and want to call the method initialize() on top of that"
            )
        else:
            if self.is_initialized is True and force is True:
                # logging.info
                print(
                    f"The usecase '{self.name}' is already initialized but argument `force=True` was provided, reinitializing..."
                )
                self.days = None

            if num_days is not None:
                self.__num_days = num_days
                if self.days is not None:
                    # logging.error
                    print(
                        f"You want to initialize the usecase '{self.name}' with num_days but you already have provided days. This might be the case if you use UseCase.load() before you used UseCase.initialize()"
                    )
                    self.__num_days = None

            if self.date_start is not None and self.date_end is not None:
                # TODO add one extra day
                self.days = generate_date_range(
                    start_date=self.date_start, end_date=self.date_end
                )
                if self.__num_days is not None:
                    if self.__num_days != len(self.days):
                        # logging.warning
                        print(
                            "You provided arguments 'date_start' and 'date_end' to your usecase. However you provided argument 'num_days' to 'initialize' method, this will build a date range from 'date_start' with 'num_days' days"
                        )
                        self.days = None
                    else:
                        self.__num_days = len(self.days)
                else:
                    self.__num_days = len(self.days)

            if self.__num_days is None:
                # asks the user how many days (i.e. code runs) they want
                self.__num_days = int(
                    input("please indicate the number of days to be generated: ")
                )
                print("Please wait...")

            if self.days is None:
                # TODO add 24 hours to date end in the display
                if self.date_start is not None:
                    self.days = generate_date_range(
                        start_date=self.date_start, num_days=self.__num_days
                    )
                else:
                    if self.date_end is not None:
                        self.days = generate_date_range(
                            end_date=self.date_end, num_days=self.__num_days
                        )
                        # logging info
                        print(
                            f"You will simulate {self.__num_days} day(s) from {self.days[0]} until {self.date_end+datetime.timedelta(days=1)}"
                        )

                    else:
                        self.days = generate_date_range(num_days=self.__num_days)
                        # logging info
                        print(
                            f"You will simulate {self.__num_days} day(s) from {self.days[0]} until {self.days[-1]+datetime.timedelta(days=1)}"
                        )

            else:
                print(
                    f"You will simulate {self.__num_days} day(s) from {self.days[0]} until {self.days[-1]+datetime.timedelta(days=1)}"
                )

            # Verify that each appliance has long enough power data for the simulated time
            for app in self.appliances:
                app.check_power_values(self.__num_days)

            if peak_enlarge is not None:
                self.peak_enlarge = peak_enlarge
            else:
                self.peak_time_range = self.calc_peak_time_range()
            # format datetimeindex in minutes
            self.__datetimeindex = generate_datetime_index(
                start=self.days[0],
                end=self.days[-1] + datetime.timedelta(days=1) - datetime.timedelta(minutes=1),
            )

    @property
    def is_initialized(self):
        answer = False
        if (
            self.__num_days is not None
            and self.__datetimeindex is not None
            and self.peak_time_range is not None
        ):
            answer = True
        return answer

    def calc_peak_time_range(self, peak_enlarge=None):
        """
        Calculate the peak time range, which is used to discriminate between off-peak and on-peak coincident switch-on probability
        Calculate first the overall Peak Window (taking into account all User classes).
        The peak time range corresponds to `peak time frame` variable in eq. (1) of [1]
        The peak window is just a time window in which coincident switch-on of multiple appliances assumes a higher probability than off-peak
        Within the peak window, a random peak time is calculated and then enlarged into a peak_time_range following again a random procedure

        Parameters
        ----------
        peak_enlarge: float
            percentage random enlargement or reduction of peak time range length
            corresponds to \delta_{peak} in [1], p.7

        Notes
        -----
        [1] F. Lombardi, S. Balderrama, S. Quoilin, E. Colombo,
            Generating high-resolution multi-energy load profiles for remote areas with an open-source stochastic model,
            Energy, 2019, https://doi.org/10.1016/j.energy.2019.04.097.

        Returns
        -------
        peak time range: numpy array
        """

        if peak_enlarge is None:
            peak_enlarge = self.peak_enlarge
        else:
            self.peak_enlarge = peak_enlarge

        tot_max_profile = np.zeros(1440)  # creates an empty daily profile
        # Aggregate each User's theoretical max profile to the total theoretical max
        for user in self.users:
            tot_max_profile = tot_max_profile + user.maximum_profile
        # Find the peak window within the theoretical max profile
        peak_window = np.squeeze(
            np.argwhere(tot_max_profile == np.amax(tot_max_profile))
        )
        # Within the peak_window, randomly calculate the peak_time using a gaussian distribution
        peak_time = round(
            random.normalvariate(
                mu=round(np.average(peak_window)),
                sigma=1 / 3 * (peak_window[-1] - peak_window[0]),
            )
        )
        # Rand_peak_enlarge is rounded to be at least 1 -> if rounded to 0 peak_time_range would be empty
        rand_peak_enlarge = max(
            round(
                math.fabs(
                    peak_time
                    - random.gauss(mu=peak_time, sigma=peak_enlarge * peak_time)
                )
            ),
            1,
        )
        # The peak_time is randomly enlarged based on the calibration parameter peak_enlarge
        return np.arange(peak_time - rand_peak_enlarge, peak_time + rand_peak_enlarge)

    def generate_daily_load_profiles(
        self, days=None, flat=True, cases=None, verbose=False
    ):
        """
        Iterate over the days and generate a daily profile for each of the days

        Parameters
        ----------
        days: datetimeindex, optional
            a list of days for which to generate daily profiles, if None, then self.days is used instead
        flat: boolean, optional
            flatten the daily profiles into a 1 dimensional array via reshaping
        cases: iterable, optional
            a list of label of the different cases. This is used if one would like to compare several independent runs
            of a ramp UseCase instance, in that case the method returns a ramp.Plot object
        verbose: boolean, optional

        Returns
        -------
        daily_profiles: numpy array
        """
        if self.days is None:
            if days is not None:
                self.days = days  # TODO this might be wrong need to update the date_start, end num_days etc
            else:
                raise ValueError(
                    "You must provide days either with start and end date and run initialize() method of UseCase instance or as an argument of 'generate_daily_load_profiles'"
                )
        if self.parallel_processing is True:
            daily_profiles = self.generate_daily_load_profiles_parallel(flat=False)
        else:
            daily_profiles = np.zeros((self.num_days, 1440))
            for day_idx, day in enumerate(self.days):
                # initialise an empty daily profile (or profile load)
                # that will be filled with the sum of the daily profiles of each User instance
                usecase_load = np.zeros(1440)
                # for each User instance generate a load profile, iterating through all user of this instance and
                # all appliances they own, corresponds to step 2. of [1], p.7
                for user in self.users:
                    user.generate_aggregated_load_profile(
                        day_idx, self.peak_time_range, get_day_type(day)
                    )
                    # aggregate the user load to the usecase load
                    usecase_load = usecase_load + user.load
                daily_profiles[day_idx, :] = usecase_load
                # screen update about progress of computation
                if verbose is True:
                    # logging.info
                    print("Day", day_idx + 1, "/", self.num_days, "completed")

        if flat is True:
            answer = daily_profiles.reshape(1, self.num_days * 1440).squeeze()
        else:
            answer = daily_profiles
        return answer


class User:
    def __init__(
        self,
        user_name: str = "",
        num_users: int = 1,
        user_preference: int = 0,
        usecase=None,
    ):
        """Creates a User instance (User Category)

        Parameters
        ----------
        user_name : str, optional
            name of the user type, by default ""
        num_users : int, optional
            number of users within the resprective user-type, by default 1
        user_preference : int {0,1,2,3}, optional
            Related to cooking behaviour, how many types of meal a user wants a day (number of user preferences has to be defined here and will be further specified with pref_index parameter), by default 0
        """
        # TODO check type of Usecase
        self.usecase = usecase
        self.user_name = user_name
        self.num_users = num_users
        self.user_preference = user_preference
        self.rand_daily_pref = 0
        self.load = None
        self.App_list = (
            []
        )  # each instance of User (i.e. each user class) has its own list of Appliances

    def __str__(self):
        try:
            return self.save()[
                ["user_name", "num_users", "name", "number", "power"]
            ].to_string()

        except Exception:
            return f"""
user_name: {self.user_name} \n
num_users: {self.num_users} \n
appliances: no appliances assigned to the user.
                    """

    def __repr__(self):
        return self.__str__()

    def _add_appliance_instance(self, appliances):
        if isinstance(appliances, Appliance):
            appliances = [appliances]
        for app in appliances:
            if not isinstance(app, Appliance):
                raise TypeError(
                    f"You are trying to add an object of type {type(app)} as an appliance to the user {self.user_name}"
                )
            if app not in self.App_list:
                if app.name == "":
                    app.name = f"appliance_{len(self.App_list) + 1}"
                self.App_list.append(app)

    def add_appliance(self, *args, **kwargs):
        """Adds an appliance to the user category with all the appliance characteristics in a single function

        Parameters
        ----------
        number : int, optional
            number of appliances of the specified kind, by default 1

        power : Union[float.pd.DataFrame], optional
            Power rating of appliance (average). If the appliance has variant daily power, a series (with the size of 366) can be passed., by default 0

        num_windows : int [1,2,3], optional
            Number of distinct time windows, by default 1

        func_time : int[0,1440], optional
            total time (minutes) the appliance is on during the day (not dependant on windows). Acceptable values are in range 0 to 1440, by default 0

        time_fraction_random_variability : Percentage, optional
            percentage of total time of use that is subject to random variability. For time (not for windows), randomizes the total time the appliance is on, by default 0

        func_cycle : int[0,1440], optional
            minimum time(minutes) the appliance is kept on after switch-on event, by default 1

        fixed : str, optional
            if 'yes', all the 'n' appliances of this kind are always switched-on together, by default "no"

        fixed_cycle : int{0,1,2,3,4}, optional
            Number of duty cycle, 0 means continuous power, if not 0 you have to fill the cw (cycle window) parameter (you may define up to 3 cws), by default 0

        occasional_use : Percentage, optional
            Defines how often the appliance is used, e.g. every second day will be 0.5, by default 1

        flat : str{'yes','no'}, optional
            allows to model appliances that are not subject to any kind of random variability, such as public lighting, by default "no"

        thermal_p_var : Percentage, optional
            Range of change of the power of the appliance (e.g. shower not taken at same temparature) or for the power of duty cycles (e.g. for a cooker, AC, heater if external temperature is different…), by default 0

        pref_index : int{0,1,2,3}, optional
            defines preference index for association with random User daily preference behaviour.This number must be smaller or equal to the value input in user_preference, by default 0

        wd_we_type : int{0,1,2}, optional
            Specify whether the appliance is used only on weekdays (0), weekend (1) or the whole week (2), by default 2

        name : str, optional
            the name of the appliance, by default ""


        Returns
        -------
        Appliance
            returns the appliance instance
        """

        # parse the args into the kwargs
        if len(args) > 0:
            if isinstance(args[0], Appliance):
                # if the first argument is an Appliance instance, it is assumed all arguments are
                # if this is not the case, error will be thrown by _add_appliance_instance method
                self._add_appliance_instance(args)
                return
            for a_name, a_val in zip(APPLIANCE_ARGS, args):
                # TODO here we could do validation of the arguments
                kwargs[a_name] = a_val

        # collects windows arguments
        windows_args = {}
        for k in WINDOWS_PARAMETERS:
            if k in kwargs:
                windows_args[k] = kwargs.pop(k)

        # collects duty cycles arguments
        duty_cycle_parameters = {}
        for i, duty_cycle_params in enumerate(DUTY_CYCLE_PARAMETERS):
            cycle_parameters = {}
            for k in duty_cycle_params:
                if k in kwargs:
                    cycle_parameters[k] = kwargs.pop(k)
            if cycle_parameters:
                duty_cycle_parameters[i + 1] = cycle_parameters

        app = Appliance(self, **kwargs)

        if windows_args:
            app.windows(**windows_args)
        for i in duty_cycle_parameters:
            app.specific_cycle(i, **duty_cycle_parameters[i])

        self._add_appliance_instance(app)

        return app

    @property
    def maximum_profile(self) -> np.array:
        """Aggregate the theoretical maximal profiles of each appliance of the user by switching the appliance always on

        Returns
        --------
        np.array
        """
        user_max_profile = np.zeros(1440)
        for appliance in self.App_list:
            # Calculate windows curve, i.e. the theoretical maximum curve that can be obtained, for each app, by switching-on always all the 'n' apps altogether in any time-step of the functioning windows
            app_max_profile = (
                appliance.maximum_profile
            )  # this computes the curve for the specific App
            user_max_profile = np.vstack(
                [user_max_profile, app_max_profile]
            )  # this stacks the specific App curve in an overall curve comprising all the Apps within a User class
        return np.transpose(np.sum(user_max_profile, axis=0)) * self.num_users

    @property
    def num_days(self):
        answer = 366
        if self.usecase is not None:
            if self.usecase.is_initialized is True:
                answer = self.usecase.num_days
        return answer

    def __eq__(self, other_user):
        """Compare two users

        ensure they have the same properties
        ensure they have the same appliances
        """
        answer = np.array([])
        for attribute in ("user_name", "num_users", "user_preference"):
            if hasattr(self, attribute) and hasattr(other_user, attribute):
                np.append(
                    answer, [getattr(self, attribute) == getattr(other_user, attribute)]
                )
            else:
                print(f"Problem with {attribute} of user")
                np.append(answer, False)
        answer = answer.all()

        if answer is True:
            # user attributes match, continue to compare each appliance
            if len(self.App_list) == len(other_user.App_list):
                answer = np.array([])
                for my_appliance, their_appliance in zip(
                    self.App_list, other_user.App_list
                ):
                    temp = my_appliance == their_appliance
                    answer = np.append(answer, temp)
                if len(answer) > 0:
                    answer = answer.all()
                else:
                    if len(self.App_list) > 0:
                        answer = False
                    else:
                        # both users have no appliances
                        answer = True
            else:
                print(
                    f"The user {self.user_name} and {other_user.user_name} do not have the same number of appliances"
                )
                answer = False
        return answer

    def Appliance(
        self,
        number=1,
        power=0,
        num_windows=1,
        func_time=0,
        time_fraction_random_variability=0,
        func_cycle=1,
        fixed="no",
        fixed_cycle=0,
        occasional_use=1,
        flat="no",
        thermal_P_var=0,
        pref_index=0,
        wd_we_type=2,
        name="",
    ):
        """Back-compatibility with legacy code

        Notes
        ------
        refer to Appliance class docs
        """

        return self.add_appliance(
            number=number,
            power=power,
            num_windows=num_windows,
            func_time=func_time,
            time_fraction_random_variability=time_fraction_random_variability,
            func_cycle=func_cycle,
            fixed=fixed,
            fixed_cycle=fixed_cycle,
            occasional_use=occasional_use,
            flat=flat,
            thermal_p_var=thermal_P_var,
            pref_index=pref_index,
            wd_we_type=wd_we_type,
            name=name,
        )

    def generate_single_load_profile(
        self, prof_i: int = 0, peak_time_range: np.array = None, day_type: int = 0
    ):
        """Generates a load profile for a single user taking all its appliances into consideration

        Parameters
        ----------
        prof_i: int[0,366]
            ith profile (day) requested by the user. 0 is the first day of the year and 365 is the last day.

        peak_time_range: np.array
            randomised peak time range calculated using calc_peak_time_range function.

        day_type: int[0,1]
            type of the ith profile. 0 for a week day or 1 for a weekend day

        Returns
        --------
        np.array
            load profile for the requested day
        """

        if peak_time_range is None:
            if self.usecase is None:
                # logging warning
                print(
                    "You are generating ramp demand from a User not bounded to a UseCase instance, a default one has been created for you "
                )
                UseCase(name=f"{self.user_name} default usecase", users=[self])
                self.usecase.peak_time_range = self.usecase.calc_peak_time_range()
            peak_time_range = self.usecase.peak_time_range

        single_load = np.zeros(1440)

        self.rand_daily_pref = (
            0 if self.user_preference == 0 else random.randint(1, self.user_preference)
        )

        for (
            App
        ) in self.App_list:  # iterates for all the App types in the given User class
            App.generate_load_profile(
                prof_i, peak_time_range, day_type, power=App.power[prof_i]
            )

            single_load = (
                single_load + App.daily_use
            )  # adds the Appliance load profile to the single User load profile
        return single_load

    def generate_aggregated_load_profile(
        self, prof_i=0, peak_time_range=None, day_type=0
    ):
        """Generates an aggregated load profile from single load profile of each user


        Parameters
        ----------

        prof_i: int[0,366]
            ith profile (day) requested by the user. 0 is the first day of the year and 365 is the last day.
        peak_time_range: numpy array
            randomised peak time range calculated using calc_peak_time_range function
        day_type: int[0,1]
            type of the ith profile. 0 for a week day or 1 for a weekend day

        Returns
        --------
        np.array
            load profile for the requested day

        Notes
        ------
        Each single load profile has its own separate randomisation
        """

        self.load = np.zeros(1440)  # initialise empty load for User instance
        for _ in range(self.num_users):
            # iterates for every single user within a User class.
            self.load = self.load + self.generate_single_load_profile(
                prof_i, peak_time_range, day_type
            )

        return self.load


class Appliance:
    def __init__(
        self,
        user,
        number: int = 1,
        power: int = 0,
        num_windows: int = 1,
        func_time: int = 0,
        time_fraction_random_variability: float = 0,
        func_cycle: int = 1,
        fixed: str = "no",
        fixed_cycle: int = 0,
        continuous_duty_cycle: int = 1,
        occasional_use: float = 1,
        flat: str = "no",
        thermal_p_var: int = 0,
        pref_index: int = 0,
        wd_we_type: int = 2,
        name: str = "",
    ):
        """Creates an appliance for a given user

        Parameters
        ----------
        user : ramp.User
            user to which the appliance is bounded

        number : int, optional
            number of appliances of the specified kind, by default 1

        power : Union[float.pd.DataFrame], optional
            Power rating of appliance (average). If the appliance has variant daily power, a series (with the size of 366) can be passed., by default 0

        num_windows : int [1,2,3], optional
            Number of distinct time windows, by default 1

        func_time : int[0,1440], optional
            total time (minutes) the appliance is on during the day (not dependant on windows). Acceptable values are in range 0 to 1440, by default 0

        time_fraction_random_variability : Percentage, optional
            percentage of total time of use that is subject to random variability. For time (not for windows), randomizes the total time the appliance is on, by default 0

        func_cycle : int[0,1440], optional
            minimum time(minutes) the appliance is kept on after switch-on event, by default 1

        continuous_duty_cycle : int[0,1], optional
            if value is 0 : the duty cycle is executed once per switch on event (like a
            welder, or other productive use appliances)
            if value is 1 : whether the duty cycle are filling the whole switch on event of
            the appliance (like a fridge or other continuous use appliance)
            by default 1

        fixed : str, optional
            if 'yes', all the 'n' appliances of this kind are always switched-on together, by default "no"

        fixed_cycle : int{0,1,2,3,4}, optional
            Number of duty cycle, 0 means continuous power, if not 0 you have to fill the cw (cycle window) parameter (you may define up to 3 cws), by default 0

        occasional_use : Percentage, optional
            Defines how often the appliance is used, e.g. every second day will be 0.5, by default 1

        flat : str{'yes','no'}, optional
            allows to model appliances that are not subject to any kind of random variability, such as public lighting, by default "no"

        thermal_p_var : Percentage, optional
            Range of change of the power of the appliance (e.g. shower not taken at same temparature) or for the power of duty cycles (e.g. for a cooker, AC, heater if external temperature is different…), by default 0

        pref_index : int{0,1,2,3}, optional
            defines preference index for association with random User daily preference behaviour.This number must be smaller or equal to the value input in user_preference, by default 0

        wd_we_type : int{0,1,2}, optional
            Specify whether the appliance is used only on weekdays (0), weekend (1) or the whole week (2), by default 2

        name : str, optional
            the name of the appliance, by default ""

        Raises
        --------
        ValueError
            1. if power is not passed as a number of series.
            2. power array size is not (366,1)
        """

        self.user = user
        self.name = name
        self.number = number
        self.num_windows = num_windows

        self.func_time = func_time
        self.time_fraction_random_variability = time_fraction_random_variability
        self.func_cycle = func_cycle
        self.fixed = fixed
        self.fixed_cycle = fixed_cycle
        self.continuous_duty_cycle = continuous_duty_cycle
        self.occasional_use = occasional_use
        self.flat = flat
        self.thermal_p_var = thermal_p_var
        self.pref_index = pref_index
        self.wd_we_type = wd_we_type

        self.__constant_power = False

        power = power * np.ones(self.user.num_days + 1)
        self.__constant_power = True

        self.power = power

        # attributes initialized by self.windows
        self.random_var_w = 0
        self.window_1 = np.array([0, 0])
        self.window_2 = np.array([0, 0])
        self.window_3 = np.array([0, 0])
        self.random_var_1 = 0
        self.random_var_2 = 0
        self.random_var_3 = 0
        self.daily_use = np.zeros(1440)
        self.free_spots = None

        # attributes used for specific fixed and random cycles
        self.p_11 = 0
        self.p_12 = 0
        self.t_11 = 0
        self.t_12 = 0
        self.r_c1 = 0
        self.p_21 = 0
        self.p_22 = 0
        self.t_21 = 0
        self.t_22 = 0
        self.r_c2 = 0
        self.p_31 = 0
        self.p_32 = 0
        self.t_31 = 0
        self.t_32 = 0
        self.r_c3 = 0

        # attribute used for cycle_behaviour
        self.cw11 = np.array([0, 0])
        self.cw12 = np.array([0, 0])
        self.cw21 = np.array([0, 0])
        self.cw22 = np.array([0, 0])
        self.cw31 = np.array([0, 0])
        self.cw32 = np.array([0, 0])

        self.random_cycle1 = np.array([])
        self.random_cycle2 = np.array([])
        self.random_cycle3 = np.array([])

        # attribute used to know if a switch on event falls within a given duty cycle window
        # if it is 0, then no switch on events happen within any duty cycle windows
        self.current_duty_cycle_id = 0

    def check_power_values(self, num_days):
        if len(self.power) < num_days:
            if self.__constant_power is True:
                self.power = self.power[0] * np.ones(num_days + 1)
            else:
                raise ValueError(
                    f"Wrong number of values for appliance '{self.name}''s power of user {self.user.user_name}: {len(self.power)}. Number of values should at least match the total number of days: {num_days}. Alternatively the power of the appliance can be set to a constant value."
                )

    def __repr__(self):
        try:
            return self.save()[
                ["user_name", "num_users", "name", "number", "power"]
            ].to_string()
        except Exception:
            return ""

    def __eq__(self, other_appliance) -> bool:
        """checks the equality of two appliances

        Returns
        -------
        bool
            True if the two appliances:
                1. have the same attributes
                2. all their attributes have the same value
        """
        answer = np.array([])
        for attribute in APPLIANCE_ATTRIBUTES:
            if hasattr(self, attribute) and hasattr(other_appliance, attribute):
                answer = np.append(
                    answer,
                    [getattr(self, attribute) == getattr(other_appliance, attribute)],
                )
            elif (
                hasattr(self, attribute) is False
                and hasattr(other_appliance, attribute) is False
            ):
                answer = np.append(answer, [True])
            else:
                if hasattr(self, attribute) is False:
                    print(f"{attribute} of appliance {self.name} is not assigned")
                else:
                    print(
                        f"{attribute} of appliance {other_appliance.name} is not assigned"
                    )
                answer = np.append(answer, [False])
        return answer.all()

    def windows(
        self,
        window_1: Iterable = None,
        window_2: Iterable = None,
        random_var_w: float = 0,
        window_3: Iterable = None,
    ):
        """assings functioning windows to the appliance and adds the appliance to the user class

        Parameters
        ----------
        window_1 : Iterable, optional
            First functioning window, by default None

        window_2 : Iterable, optional
            Second functioning window, by default None

        window_3 : Iterable, optional
            Third functioning window, by default None

        random_var_w : Percentage, optional
            variability of the windows in percent, the same for all windows, by default 0

        Raises
        ------
        InvalidWindow

            * If number of specifies windows does not correspond to the given functioning windows.
            * If the sum of all windows time intervals for the appliance is smaller than the time the appliance is supposed to be on.

        Example
        --------
        If three time window is specified for the appliance as follow:

        #. from 00:00:00 to 00:20:00
        #. from 00:30:00 to 00:35:00
        #. from 00:40:00 to 00:55:00

        .. code-block:: python

            user.windows(
                window_1 = [0,20],
                window_2 = [30,35],
                window_3 = [40,55]
            )
        """

        if window_1 is None:
            self.window_1 = np.array([0, 1440])
        else:
            self.window_1 = window_1

        if window_2 is None:
            if self.num_windows >= 2:
                raise InvalidWindow(
                    "Windows 2 is not provided although 2 windows were declared"
                )
        else:
            self.window_2 = window_2

        if window_3 is None:
            if self.num_windows == 3:
                raise InvalidWindow(
                    "Windows 3 is not provided although 3 windows were declared"
                )
        else:
            self.window_3 = window_3

        # check that the time allocated by the windows is larger or equal to the func_time of the appliance
        window_time = 0
        for i in range(1, self.num_windows + 1, 1):
            window_time = window_time + np.diff(getattr(self, f"window_{i}"))[0]
        if window_time < self.func_time:
            raise ValueError(
                f"The sum of all windows time intervals for the appliance '{self.name}' of user '{self.user.user_name}' is smaller than the time the appliance is supposed to be on ({window_time} < {self.func_time}). Please check your input file for typos."
            )

        self.random_var_w = random_var_w
        self.daily_use = np.zeros(1440)  # create an empty daily use profile
        self.daily_use[self.window_1[0] : (self.window_1[1])] = np.full(
            np.diff(self.window_1), 0.001
        )  # fills the daily use profile with infinitesimal values that are just used to identify the functioning windows
        self.daily_use[self.window_2[0] : (self.window_2[1])] = np.full(
            np.diff(self.window_2), 0.001
        )  # same as above for window2
        self.daily_use[self.window_3[0] : (self.window_3[1])] = np.full(
            np.diff(self.window_3), 0.001
        )  # same as above for window3

        self.random_var_1 = int(
            random_var_w * np.diff(self.window_1)[0]
        )  # calculate the random variability of window1, i.e. the maximum range of time they can be enlarged or shortened
        self.random_var_2 = int(
            random_var_w * np.diff(self.window_2)[0]
        )  # same as above
        self.random_var_3 = int(
            random_var_w * np.diff(self.window_3)[0]
        )  # same as above

        # automatically appends the appliance to the user's appliance list
        self.user._add_appliance_instance(self)

        if self.fixed_cycle == 1:
            self.cw11 = self.window_1
            self.cw12 = self.window_2

    def assign_random_cycles(self):
        """
        Calculates randomised cycles taking the random variability in the duty cycle duration
        """
        if self.fixed_cycle >= 1:
            p_11 = random_variation(
                var=self.thermal_p_var, norm=self.p_11
            )  # randomly variates the power of thermal apps, otherwise variability is 0
            p_12 = random_variation(
                var=self.thermal_p_var, norm=self.p_12
            )  # randomly variates the power of thermal apps, otherwise variability is 0
            self.random_cycle1 = duty_cycle(
                var=self.r_c1, t1=self.t_11, p1=p_11, t2=self.t_12, p2=p_12
            )  # randomise also the fixed cycle
            self.random_cycle2 = self.random_cycle1
            self.random_cycle3 = self.random_cycle1
            if self.fixed_cycle >= 2:
                p_21 = random_variation(
                    var=self.thermal_p_var, norm=self.p_21
                )  # randomly variates the power of thermal apps, otherwise variability is 0
                p_22 = random_variation(
                    var=self.thermal_p_var, norm=self.p_22
                )  # randomly variates the power of thermal apps, otherwise variability is 0
                self.random_cycle2 = duty_cycle(
                    var=self.r_c2, t1=self.t_21, p1=p_21, t2=self.t_22, p2=p_22
                )  # randomise also the fixed cycle

                if self.fixed_cycle >= 3:
                    p_31 = random_variation(
                        var=self.thermal_p_var, norm=self.p_31
                    )  # randomly variates the power of thermal apps, otherwise variability is 0
                    p_32 = random_variation(
                        var=self.thermal_p_var, norm=self.p_32
                    )  # randomly variates the power of thermal apps, otherwise variability is 0
                    self.random_cycle1 = random_choice(
                        self.r_c1, t1=self.t_11, p1=p_11, t2=self.t_12, p2=p_12
                    )

                    self.random_cycle2 = random_choice(
                        self.r_c2, t1=self.t_21, p1=p_21, t2=self.t_22, p2=p_22
                    )

                    self.random_cycle3 = random_choice(
                        self.r_c3, t1=self.t_31, p1=p_31, t2=self.t_32, p2=p_32
                    )

    def update_available_time_for_switch_on_events(self, indexes):
        """Remove the given time indexes from the ranges available to switch appliance on

        Parameters
        ----------
        indexes: list of int
            time indexes of the daily profile concerned by a new switch-on event

        Return
        ------
        nothing but can modify self.free_spots
        """
        # identify which of the unallocated time ranges contain the switch-on event
        spot_idx = None
        for i, fs in enumerate(self.free_spots):
            if indexes[0] >= fs.start and indexes[-1] <= fs.stop:
                spot_idx = i
                break
        if spot_idx is not None:
            spot_to_split = self.free_spots.pop(spot_idx)

            if indexes[0] == spot_to_split.start and indexes[-1] == spot_to_split.stop:
                pass  # nothing to do as the whole range should be removed, which is already the case from line above
            elif indexes[0] == spot_to_split.start:
                # reinsert a range going from end of indexes up to the end of picked range
                self.free_spots.insert(
                    spot_idx, slice(indexes[-1] + 1, spot_to_split.stop, None)
                )
            elif indexes[-1] == spot_to_split.stop:
                # reinsert a range going from beginning of picked range up to the beginning of indexes
                self.free_spots.insert(
                    spot_idx, slice(spot_to_split.start, indexes[0], None)
                )
            else:
                # split the range into 2 smaller ranges
                new_spot1 = slice(spot_to_split.start, indexes[0], None)
                new_spot2 = slice(indexes[-1] + 1, spot_to_split.stop, None)

                self.free_spots.insert(spot_idx, new_spot2)
                self.free_spots.insert(spot_idx, new_spot1)

    def update_daily_use(self, coincidence, power, indexes):
        """Update the daily use depending on existence of duty cycles of the Appliance instance

        This corresponds to step 2d. and 2e. of [1]

        [1] F. Lombardi, S. Balderrama, S. Quoilin, E. Colombo,
            Generating high-resolution multi-energy load profiles for remote areas with an open-source stochastic model,
            Energy, 2019, https://doi.org/10.1016/j.energy.2019.04.097.

        """

        if (
            self.fixed_cycle > 0
        ):  # evaluates if the app has some duty cycles to be considered
            # the proper duty cycle was selected in self.rand_switch_on_window()
            # now setting the corresponding power values in the indexes range
            if self.current_duty_cycle_id == 1:
                np.put(self.daily_use, indexes, (self.random_cycle1 * coincidence))
            elif self.current_duty_cycle_id == 2:
                np.put(self.daily_use, indexes, (self.random_cycle2 * coincidence))
            elif self.current_duty_cycle_id == 3:
                np.put(self.daily_use, indexes, (self.random_cycle3 * coincidence))
            else:
                print(
                    f"The app {self.name} has duty cycle option on, however the switch on event fell outside the provided duty cycle windows"
                )

        else:  # if no duty cycles are specified, a regular switch_on event is modelled
            # randomises also the App Power if thermal_p_var is on
            np.put(
                self.daily_use,
                indexes,
                (random_variation(var=self.thermal_p_var, norm=coincidence * power)),
            )
        # updates the time ranges remaining for switch on events, excluding the current switch_on event
        self.update_available_time_for_switch_on_events(indexes)

    def calc_rand_window(self, window_idx=1, window_range_limits=[0, 1440]):
        _window = self.__getattribute__(f"window_{window_idx}")
        _random_var = self.__getattribute__(f"random_var_{window_idx}")
        rand_window = [
            random.randint(_window[0] - _random_var, _window[0] + _random_var),
            random.randint(_window[1] - _random_var, _window[1] + _random_var),
        ]
        if rand_window[0] < window_range_limits[0]:
            rand_window[0] = window_range_limits[0]
        if rand_window[1] > window_range_limits[1]:
            rand_window[1] = window_range_limits[1]

        return rand_window

    @property
    def maximum_profile(self):
        """Virtual maximum load profile of the appliance

        Returns
        --------
        np.array
            It assumes the appliance is always switched-on with maximum power and
            numerosity during all of its potential windows of use
        """
        return self.daily_use * np.mean(self.power) * self.number

    def specific_cycle(self, cycle_num, **kwargs):
        """assigining specific duty cycle for the appliance (maximum of three cycles can be assigned)

        Parameters
        ----------
        cycle_num : int
            represents the number of the specific cycle to be assigned. acceptable values are [1,2,3]

        **kwargs :
            additional features passed tp each specific cycle function. For example iff cycle_num = 1, **kwargs represents the arguments of function 'specific_cycle_1' which are:
                * p_11
                * t_11
                * p_12
                * t_12
                * r_c1
                * cw11
                * cw12
        """
        if cycle_num == 1:
            self.specific_cycle_1(**kwargs)
        elif cycle_num == 2:
            self.specific_cycle_2(**kwargs)
        elif cycle_num == 3:
            self.specific_cycle_3(**kwargs)

    def specific_cycle_1(
        self, p_11=0, t_11=0, p_12=0, t_12=0, r_c1=0, cw11=None, cw12=None
    ):
        """assigining the frist specific duty cycle for the appliace (maximum of three cycles can be assigned)

        Parameters
        ----------
        p_11 : float, optional
            Power rating for first part of first duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        t_11 : int[0,1440], optional
            Duration (minutes) of first part of first duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        p_12 : int, float, optional
            Power rating for second part of first duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        t_12 : int[0,1440], optional
            Duration (minutes) of second part of first duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        r_c1 : Percentage [0,1], optional
            randomization of the duty cycle parts duration. There will be a uniform random variation around t_i1 and t_i2. If this parameter is set to 0.1, then t_i1 and t_i2 will be randomly reassigned between 90% and 110% of their initial value; 0 means no randomisation, by default 0

        cw11 : Iterable, optional
            Window time range for the first part of first duty cycle number (not neccessarily linked to the overall time window), by default None

        cw12 : Iterable, optional
            Window time range for the first part of first duty cycle number (not neccessarily linked to the overall time window), by default None, by default None
        """
        self.p_11 = p_11
        self.t_11 = int(t_11)
        self.p_12 = p_12
        self.t_12 = int(t_12)
        self.r_c1 = r_c1
        if cw11 is not None:
            self.cw11 = cw11
        if cw12 is not None:
            self.cw12 = cw12
        # Below is not used
        self.fixed_cycle1 = np.concatenate(
            ((np.ones(self.t_11) * p_11), (np.ones(self.t_12) * p_12))
        )  # create numpy array representing the duty cycle

    def specific_cycle_2(
        self, p_21=0, t_21=0, p_22=0, t_22=0, r_c2=0, cw21=None, cw22=None
    ):
        """assigining the frist specific duty cycle for the appliace (maximum of three cycles can be assigned)

        Parameters
        ----------
        p_21 : float, optional
            Power rating for first part of second duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        t_21 : int[0,1440], optional
            Duration (minutes) of first part of second duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        p_22 : int, float, optional
            Power rating for second part of second duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        t_22 : int[0,1440], optional
            Duration (minutes) of second part of second duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        r_c2 : Percentage [0,1], optional
            randomization of the duty cycle parts duration. There will be a uniform random variation around t_i1 and t_i2. If this parameter is set to 0.1, then t_i1 and t_i2 will be randomly reassigned between 90% and 110% of their initial value; 0 means no randomisation, by default 0

        cw21 : Iterable, optional
            Window time range for the first part of second duty cycle number (not neccessarily linked to the overall time window), by default None

        cw22 : Iterable, optional
            Window time range for the first part of second duty cycle number (not neccessarily linked to the overall time window), by default None, by default None
        """
        self.p_21 = p_21
        self.t_21 = int(t_21)
        self.p_22 = p_22
        self.t_22 = int(t_22)
        self.r_c2 = r_c2
        if cw21 is not None:
            self.cw21 = cw21
        if cw22 is not None:
            self.cw22 = cw22
        # Below is not used
        self.fixed_cycle2 = np.concatenate(
            ((np.ones(self.t_21) * p_21), (np.ones(self.t_22) * p_22))
        )

    def specific_cycle_3(
        self, p_31=0, t_31=0, p_32=0, t_32=0, r_c3=0, cw31=None, cw32=None
    ):
        """assigining the frist specific duty cycle for the appliace (maximum of three cycles can be assigned)

        Parameters
        ----------
        p_31 : float, optional
            Power rating for first part of third duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        t_31 : int[0,1440], optional
            Duration (minutes) of first part of third duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        p_32 : int, float, optional
            Power rating for second part of third duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        t_32 : int[0,1440], optional
            Duration (minutes) of second part of third duty cycle. Only necessary if fixed_cycle is set to 1 or greater, by default 0

        r_c3 : Percentage [0,1], optional
            randomization of the duty cycle parts duration. There will be a uniform random variation around t_i1 and t_i2. If this parameter is set to 0.1, then t_i1 and t_i2 will be randomly reassigned between 90% and 110% of their initial value; 0 means no randomisation, by default 0

        cw31 : Iterable, optional
            Window time range for the first part of third duty cycle number (not neccessarily linked to the overall time window), by default None

        cw32 : Iterable, optional
            Window time range for the first part of third duty cycle number (not neccessarily linked to the overall time window), by default None, by default None
        """
        self.p_31 = p_31
        self.t_31 = int(t_31)
        self.p_32 = p_32
        self.t_32 = int(t_32)
        self.r_c3 = r_c3
        if cw31 is not None:
            self.cw31 = cw31
        if cw32 is not None:
            self.cw32 = cw32
        # Below is not used
        self.fixed_cycle3 = np.concatenate(
            ((np.ones(self.t_31) * p_31), (np.ones(self.t_32) * p_32))
        )

    # different time windows can be associated with different specific duty cycles
    def cycle_behaviour(
        self,
        cw11=np.array([0, 0]),
        cw12=np.array([0, 0]),
        cw21=np.array([0, 0]),
        cw22=np.array([0, 0]),
        cw31=np.array([0, 0]),
        cw32=np.array([0, 0]),
    ):
        """_summary_

        Parameters
        ----------
        cw11 : Iterable, optional
            Window time range for the first part of first duty cycle number, by default np.array([0,0])
        cw12 : Iterable, optional
            Window time range for the second part of first duty cycle number, by default np.array([0,0])
        cw21 : Iterable, optional
            Window time range for the first part of second duty cycle number, by default np.array([0,0])
        cw22 : Iterable, optional
            Window time range for the second part of second duty cycle number, by default np.array([0,0])
        cw31 : Iterable, optional
            Window time range for the first part of third duty cycle number, by default np.array([0,0])
        cw32 : Iterable, optional
            Window time range for the second part of third duty cycle number, by default np.array([0,0])
        """
        # only used around line 223
        self.cw11 = cw11  # first window associated with cycle1
        self.cw12 = cw12  # second window associated with cycle1
        self.cw21 = cw21  # same for cycle2
        self.cw22 = cw22
        self.cw31 = cw31  # same for cycle 3
        self.cw32 = cw32

    def rand_total_time_of_use(
        self,
        rand_window_1: Iterable[int],
        rand_window_2: Iterable[int],
        rand_window_3: Iterable[int],
    ) -> int:
        """Randomised total time of use of the Appliance instance"""

        random_var_t = random_variation(var=self.time_fraction_random_variability)

        rand_time = round(
            random.uniform(self.func_time, int(self.func_time * random_var_t))
        )

        if rand_time < self.func_cycle:
            rand_time = self.func_cycle

        # total time available for appliance usage
        total_time = (
            (rand_window_1[1] - rand_window_1[0])
            + (rand_window_2[1] - rand_window_2[0])
            + (rand_window_3[1] - rand_window_3[0])
        )

        # check that the total randomised time of use does not exceed the total time available
        if rand_time > 0.99 * total_time:
            rand_time = int(0.99 * total_time)

        if rand_time < self.func_cycle:
            raise ValueError(
                f"The func_cycle you choose for appliance {self.name} might be too large to fit in the available time for appliance usage, please either reduce func_cycle or increase the windows of use of the appliance"
            )
        return rand_time

    def rand_switch_on_window(self, rand_time: int):
        """Identifies a random switch on window within the available functioning windows

        This corresponds to step 2c. of:

            F. Lombardi, S. Balderrama, S. Quoilin, E. Colombo,
            Generating high-resolution multi-energy load profiles for remote areas with an open-source stochastic model,
            Energy, 2019, https://doi.org/10.1016/j.energy.2019.04.097.
        """

        indexes_choice = []
        for s in self.free_spots:
            if s.stop - s.start >= self.func_cycle:
                indexes_choice += [
                    *range(s.start, s.stop - self.func_cycle + 1)
                ]  # this will be fast with cython
        n_choices = len(indexes_choice)
        if n_choices > 0:
            # Identifies a random switch on time within the available functioning windows
            # step 2c of [1]
            switch_on = indexes_choice[random.randint(0, n_choices - 1)]
            spot_idx = None
            for i, fs in enumerate(self.free_spots):
                if fs.start <= switch_on <= fs.stop - self.func_cycle:
                    spot_idx = i
                    break

            largest_duration = min(
                rand_time, self.free_spots[spot_idx].stop - switch_on
            )

            if largest_duration > self.func_cycle:
                indexes = np.arange(
                    switch_on,
                    switch_on
                    + (int(random.uniform(self.func_cycle, largest_duration))),
                )  # TODO randint
            elif largest_duration == self.func_cycle:
                indexes = np.arange(switch_on, switch_on + largest_duration)
            else:
                print("func time", self.func_cycle)
                print("max window", self.free_spots[spot_idx].stop)
                print("rand_time", rand_time)
                print("upper_limit", largest_duration)
                raise ValueError(
                    "There is something fishy with upper limit in switch on..."
                )

            if (
                self.fixed_cycle > 0
            ):  # evaluates if the app has some duty cycles to be considered
                indexes_low = indexes[0]
                indexes_high = indexes[-1]
                # selects the proper duty cycle
                if range_within_window(
                    indexes_low, indexes_high, self.cw11
                ) or range_within_window(indexes_low, indexes_high, self.cw12):
                    self.current_duty_cycle_id = 1
                    duty_cycle_duration = len(self.random_cycle1)
                elif range_within_window(
                    indexes_low, indexes_high, self.cw21
                ) or range_within_window(indexes_low, indexes_high, self.cw22):
                    self.current_duty_cycle_id = 2
                    duty_cycle_duration = len(self.random_cycle2)
                elif range_within_window(
                    indexes_low, indexes_high, self.cw31
                ) or range_within_window(indexes_low, indexes_high, self.cw32):
                    self.current_duty_cycle_id = 3
                    duty_cycle_duration = len(self.random_cycle3)
                else:
                    # previously duty_cycle3 was always considered as default if neither duty_cycle1 nor duty_cycle2
                    # got selected. If the switch on window does not fall within any duty cycle we do not assign it
                    # to duty_cycle3 by default, rather we pick another switch on event and we notify the user we
                    # did so. That way, in case this warning is shown too often, it can indicate to the user there
                    # is some peculiar behavior for this appliance
                    return self.rand_switch_on_window(rand_time)

                if (
                    indexes.size > duty_cycle_duration
                    and self.continuous_duty_cycle == 0
                ):
                    # Limit switch_on_window to duration of duty_cycle
                    indexes = indexes[0:duty_cycle_duration]
        else:
            indexes = None
            # there are no available windows anymore

        return indexes

    def calc_coincident_switch_on(self, inside_peak_window: bool = True):
        """Computes how many of the 'n' Appliance instance are switched on simultaneously

        Implement eqs. 3 and 4 of [1]

        [1] F. Lombardi, S. Balderrama, S. Quoilin, E. Colombo,
            Generating high-resolution multi-energy load profiles for remote areas with an open-source stochastic model,
            Energy, 2019, https://doi.org/10.1016/j.energy.2019.04.097.
        """
        s_peak, mu_peak, op_factor = switch_on_parameters()

        # check if indexes are within peak window
        if inside_peak_window is True and self.fixed == "no":
            # calculates coincident behaviour within the peak time range
            # eq. 4 of [1]
            coincidence = min(
                self.number,
                max(
                    1,
                    math.ceil(
                        random.gauss(
                            mu=(self.number * mu_peak),
                            sigma=(s_peak * self.number * mu_peak),
                        )
                    ),
                ),
            )
        # check if indexes are off-peak
        elif inside_peak_window is False and self.fixed == "no":
            # calculates probability of coincident switch_ons off-peak
            # eq. 3 of [1]
            prob = random.uniform(0, (self.number - op_factor) / self.number)

            # randomly selects how many appliances are on at the same time
            array = np.arange(0, self.number) / self.number
            try:
                on_number = np.max(np.where(prob >= array)) + 1
            except ValueError:
                on_number = 1

            coincidence = on_number
        else:
            # All 'n' copies of an Appliance instance are switched on altogether
            coincidence = self.number
        return coincidence

    def generate_load_profile(self, prof_i, peak_time_range, day_type, power):
        """Generate load profile of the Appliance instance by updating its daily_use attribute

        Run steps 2a and 2b and repeat steps 2c - 2e of [1] until the sum of the durations of
        all the switch-on events equals the randomised total time of use of the Appliance

        [1] F. Lombardi, S. Balderrama, S. Quoilin, E. Colombo,
            Generating high-resolution multi-energy load profiles for remote areas with an open-source stochastic model,
            Energy, 2019, https://doi.org/10.1016/j.energy.2019.04.097.
        """
        # initialises variables for the cycle
        self.daily_use = np.zeros(1440)

        # skip this appliance in any of the following applies
        if (
            random.uniform(0, 1) > self.occasional_use
            # evaluates if daily preference coincides with the randomised daily preference number
            or (self.pref_index != 0 and self.user.rand_daily_pref != self.pref_index)
            # checks if the app is allowed in the given yearly behaviour pattern
            or self.wd_we_type not in [day_type, 2]
            # skip if the app has a func_time of 0
            or self.func_time == 0
        ):
            return

        # recalculate windows start and ending times randomly, based on the inputs
        rand_window_1 = self.calc_rand_window(window_idx=1)
        rand_window_2 = self.calc_rand_window(window_idx=2)
        rand_window_3 = self.calc_rand_window(window_idx=3)
        rand_windows = [rand_window_1, rand_window_2, rand_window_3]

        # random variability is applied to the total functioning time and to the duration
        # of the duty cycles provided they have been specified
        # step 2a of [1]
        rand_time = self.rand_total_time_of_use(
            rand_window_1, rand_window_2, rand_window_3
        )

        # redefines functioning windows based on the previous randomisation of the boundaries
        # step 2b of [1]
        if self.flat == "yes":
            # for "flat" appliances the algorithm stops right after filling the newly
            # created windows without applying any further stochasticity
            total_power_value = self.power[prof_i] * self.number
            for rand_window in rand_windows:
                self.daily_use[rand_window[0] : rand_window[1]] = np.full(
                    np.diff(rand_window), total_power_value
                )
            # single_load = single_load + self.daily_use
            return
        else:
            # "non-flat" appliances a mask is applied on the newly defined windows and
            # the algorithm goes further on
            for rand_window in rand_windows:
                self.daily_use[rand_window[0] : rand_window[1]] = np.full(
                    np.diff(rand_window), 0.001
                )

        # calculates randomised cycles taking the random variability in the duty cycle duration
        self.assign_random_cycles()

        # steps 2c-2e repeated until the sum of the durations of all the switch-on events equals rand_time

        self.free_spots = [
            slice(rw[0], rw[1], None) for rw in rand_windows if rw[0] != rw[1]
        ]

        tot_time = 0
        while tot_time <= rand_time and rand_time != 0:
            # one option could be to generate a lot of them at once
            indexes = self.rand_switch_on_window(
                rand_time=rand_time,  # TODO maybe only consider rand_time-tot_time ...
            )
            if indexes is None:
                break  # exit cycle and go to next Appliance as there are no available windows anymore

            # the count of total time is updated with the size of the indexes array
            tot_time = tot_time + indexes.size

            if tot_time > rand_time:
                # the total functioning time is reached, a correction is applied to avoid overflow of indexes
                indexes_adj = indexes[: -(tot_time - rand_time)]
                if len(indexes_adj) > 0:
                    inside_peak_window = within_peak_time_window(
                        indexes_adj[0],
                        indexes_adj[-1],
                        peak_time_range[0],
                        peak_time_range[-1],
                    )

                    # Computes how many of the 'n' of the Appliance instance are switched on simultaneously
                    coincidence = self.calc_coincident_switch_on(inside_peak_window)
                    # Update the daily use depending on existence of duty cycles of the Appliance instance
                    self.update_daily_use(coincidence, power=power, indexes=indexes_adj)
                break  # exit cycle and go to next Appliance

            else:
                inside_peak_window = within_peak_time_window(
                    indexes[0], indexes[-1], peak_time_range[0], peak_time_range[-1]
                )

                coincidence = self.calc_coincident_switch_on(inside_peak_window)
                # Update the daily use depending on existence of duty cycles of the Appliance instance
                self.update_daily_use(coincidence, power=power, indexes=indexes)
