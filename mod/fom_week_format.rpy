init -990 python:
    store.mas_submod_utils.Submod(
        author="Friends of Monika",
        name="Calendar Week Format",
        description=_("This submod changes MAS calendar week format."),
        version="1.0.0",
        settings_pane="fom_week_format_settings_pane"
    )

init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Calendar Week Format",
            user_name="friends-of-monika",
            repository_name="mas-week-format",
            extraction_depth=2
        )

screen fom_week_format_settings_pane():
    vbox:
        box_wrap False
        xfill True
        xmaximum 800

        if store._fom_week_format.is_mas_version_supported():
            text _("MAS version is {color=#84cc16}supported{/color}.")
            $ week_format = store._fom_week_format.WEEK_FORMATS[store._fom_week_format.get_locale_week_format_idx()]
            text _("Week format determined based on system locale: " + week_format[0])
        else:
            text _("MAS version is {color=#ef4444}unsupported{/color}!")


init 2 python in _fom_week_format:
    if is_mas_version_supported():
        set_week_format(get_locale_week_format_idx())


init 1 python in _fom_week_format:
    from store import MASCalendar
    from types import CodeType, FunctionType
    import calendar
    import dis

    SUPPORTED_VERSIONS = [
        "0.12.15",
        "0.12.16",
        "0.12.17",
        "0.12.18"
    ]

    def is_mas_version_supported():
        return renpy.config.version.split("-")[0] in SUPPORTED_VERSIONS

    def get_original_code():
        setupDayButtons_code = MASCalendar._setupDayButtons.func_code
        return CodeType(setupDayButtons_code.co_argcount,
                        setupDayButtons_code.co_nlocals,
                        setupDayButtons_code.co_stacksize,
                        setupDayButtons_code.co_flags,
                        setupDayButtons_code.co_code,
                        setupDayButtons_code.co_consts,
                        setupDayButtons_code.co_names,
                        setupDayButtons_code.co_varnames,
                        setupDayButtons_code.co_filename,
                        setupDayButtons_code.co_name,
                        setupDayButtons_code.co_firstlineno,
                        setupDayButtons_code.co_lnotab)

    WEEKDAY_BYTECODE_OFFSET = 377
    ORIGINAL_BYTECODE = get_original_code()

    def get_patched_code(new_weekday_const):
        setupDayButtons_code = ORIGINAL_BYTECODE
        setupDayButtons_consts = list(setupDayButtons_code.co_consts)

        setupDayButtons_consts.append(new_weekday_const)
        setupDayButtons_consts_idx = len(setupDayButtons_consts) - 1

        setupDayButtons_code_bytes = bytearray(setupDayButtons_code.co_code)
        setupDayButtons_code_bytes[WEEKDAY_BYTECODE_OFFSET + 1] = setupDayButtons_consts_idx & 0xFF
        setupDayButtons_code_bytes[WEEKDAY_BYTECODE_OFFSET + 2] = (setupDayButtons_consts_idx >> 8) & 0xFF

        return CodeType(setupDayButtons_code.co_argcount,
                        setupDayButtons_code.co_nlocals,
                        setupDayButtons_code.co_stacksize,
                        setupDayButtons_code.co_flags,
                        bytes(setupDayButtons_code_bytes),
                        tuple(setupDayButtons_consts),
                        setupDayButtons_code.co_names,
                        setupDayButtons_code.co_varnames,
                        setupDayButtons_code.co_filename,
                        setupDayButtons_code.co_name,
                        setupDayButtons_code.co_firstlineno,
                        setupDayButtons_code.co_lnotab)

    def get_patched_setupDayButtons(new_weekday):
        setupDayButtons = MASCalendar._setupDayButtons
        setupDayButtons_new_code = get_patched_code(new_weekday)
        return FunctionType(setupDayButtons_new_code,
                            setupDayButtons.func_globals,
                            setupDayButtons.func_name,
                            setupDayButtons.func_defaults,
                            setupDayButtons.func_closure)

    def patch_MASCalendar__setupDayButtons(new_weekday):
        new_function = get_patched_setupDayButtons(new_weekday)
        MASCalendar._setupDayButtons = new_function

    def patch_MASCalendar_DAY_NAMES(new_day_names):
        MASCalendar.DAY_NAMES = new_day_names


    WEEK_FORMATS = [
        (_("Monday - Saturday"), ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], 0),
        (_("Saturday - Sunday"), ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], 6)
    ]

    def set_week_format(format_idx):
        ui_name, names, first_day = WEEK_FORMATS[format_idx]
        patch_MASCalendar_DAY_NAMES(names)
        patch_MASCalendar__setupDayButtons(first_day)

    def get_locale_week_format_idx():
        first_weekday = calendar.firstweekday()
        if first_weekday == 0:
            return 0
        return 1 # Fallback
