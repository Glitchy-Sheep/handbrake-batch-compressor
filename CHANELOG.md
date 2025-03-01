# 3.0.0 - New flexible file handling options.

- Simplify the CLI interface by changing file-based options:
- Add options: `--ineffective-compression-behavior` and `--effective-compression-behavior`.
- Removed: `--keep-only-smaller` (now it's obsolete).

**BREAKING CHANGES:**

- Removed the `--keep-only-smaller` option. 
  Now you can specify options for handling ineffective and effective compressions instead:
  - `--ineffective-compression-behavior` 
  - `--effective-compression-behavior` 

  So the flag `--keep-only-smaller` becomes `--ineffective-compression-behavior skip`


# 2.1.0

- Enhance look of progress bars. (Add elapsed time, better formatting, panels)

# 2.0.1

- Fix a bug with encoding in utf-8.

# 2.0.0

- Added the --skip-failed-files argument to allow skipping failed compressions and continuing with the next file.
- Fixed an error handling bug in the main try/except block.
- Improved logger formatting for better readability.
- Enabled parallel capturing of stderr and stdout for HandBrakeCLI; revamped the error logging system to log only errors.
- Various minor fixes, formatting improvements, and optimizations.

# 1.1.3

- Add possibility to gracefully stop the compression process by keyboard (ctrl + c).
- More elegant error handling/logging system using custom exceptions.

# 1.1.2

- Fix the bug with crashing on videos with Variable Frame Rate (VFR)

# 1.1.1

- Remove junk log files after successful compression to not leave unnecessary traces.

# 1.1.0

- Add --version argument to show the version and exit.

# 1.0.1

- Fix readme pictures links to make it accessible on pypi.

# 1.0.0

- Add packaging with poetry.

# 0.4.0

- Add --guide argument to show basic information about the compression options.

# 0.3.2

- Add strict type checking with pyright and fix all the type errors.

# 0.3.1

- Major refactor to make the code more maintainable, testable and reusable.

# 0.3.0

- Add argument to skip unefficient file compression.

# 0.2.0:

- Add smart filters to skip unwanted files.

# 0.1.0:

- Initial release and test the idea.
- Essential features:
    - Traverse all the video files under the specified directory.
    - Compress the video files using HandBrake.
    - Remove incomplete files.
    - Log the compression stats.
