# Cobra CLI Patterns

## Project Layout

- **Root command lives in `cmd/root.go`** with global setup:
  ```go
  var rootCmd = &cobra.Command{
      Use:   "myapp",
      Short: "A brief description of your application",
  }

  func Execute() {
      if err := rootCmd.Execute(); err != nil {
          os.Exit(1)
      }
  }
  ```
- **Each subcommand gets its own file** at `cmd/<name>.go`
- **Register subcommands in `init()`** functions:
  ```go
  func init() {
      rootCmd.AddCommand(serveCmd)
  }
  ```

## Command Definition

- **Use `RunE` over `Run`** to propagate errors instead of calling `os.Exit()` directly:
  ```go
  var serveCmd = &cobra.Command{
      Use:   "serve",
      Short: "Start the HTTP server",
      RunE: func(cmd *cobra.Command, args []string) error {
          return startServer(cmd.Context())
      },
  }
  ```
- **Validate arguments with built-in validators**:
  ```go
  Args: cobra.ExactArgs(1),      // exactly one argument
  Args: cobra.MinimumNArgs(1),   // at least one argument
  Args: cobra.NoArgs,            // no positional arguments allowed
  ```

## Flags

- **Use `PersistentFlags` on root** for options shared across all subcommands:
  ```go
  rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file path")
  rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "verbose output")
  ```
- **Use `Flags` on individual commands** for command-specific options:
  ```go
  serveCmd.Flags().IntVarP(&port, "port", "p", 8080, "server port")
  ```
- **Mark required flags explicitly**:
  ```go
  serveCmd.MarkFlagRequired("port")
  ```

## Viper Integration

- **Bind flags to viper in `init()`** for config file support:
  ```go
  func init() {
      cobra.OnInitialize(initConfig)
      viper.BindPFlag("port", serveCmd.Flags().Lookup("port"))
  }

  func initConfig() {
      if cfgFile != "" {
          viper.SetConfigFile(cfgFile)
      } else {
          viper.SetConfigName(".myapp")
          viper.AddConfigPath("$HOME")
      }
      viper.AutomaticEnv()
      viper.ReadInConfig()
  }
  ```
- **Precedence order**: flags override env vars override config file override defaults
