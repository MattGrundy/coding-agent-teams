type Profile struct {
	PushWhitelist []string          `yaml:"push_whitelist"`
	Authority     map[string]*Repo  `yaml:"authority"`
}

type Repo struct {
	CanPush       bool     `yaml:"can_push"`
	PushWhitelist []string `yaml:"push_whitelist"`
}
