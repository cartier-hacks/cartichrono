{
  config,
  pkgs,
  inputs,
  hostname,
  assets,
  ...
}:
{
  # Bootloader.
  boot = {
    loader = {
      systemd-boot = {
        enable = true;
      };

      efi = {
        canTouchEfiVariables = true;
      };
    };

    # Mount my second drive
    supportedFilesystems = [ "ntfs" ];
  };

  networking = {
    hostName = hostname;

    networkmanager = {
      enable = true;
    };
  };

  time = {
    timeZone = "America/New_York";
  };

  i18n = {
    defaultLocale = "en_US.UTF-8";

    extraLocaleSettings = {
      LC_ADDRESS = "en_US.UTF-8";
      LC_IDENTIFICATION = "en_US.UTF-8";
      LC_MEASUREMENT = "en_US.UTF-8";
      LC_MONETARY = "en_US.UTF-8";
      LC_NAME = "en_US.UTF-8";
      LC_NUMERIC = "en_US.UTF-8";
      LC_PAPER = "en_US.UTF-8";
      LC_TELEPHONE = "en_US.UTF-8";
      LC_TIME = "en_US.UTF-8";
    };
  };

  services = {
    printing = {
      enable = true;
    };

    # Flatpak is here just for discord pretty much
    flatpak = {
      enable = true;
    };

    pulseaudio = {
      enable = false;
    };

    pipewire = {
      enable = true;
      alsa.enable = true;
      alsa.support32Bit = true;
      pulse.enable = true;
    };

    openssh = {
      enable = true;
    };
  };

  systemd.services.flatpak-repo = {
    wantedBy = [ "multi-user.target" ];
    path = [ pkgs.flatpak ];
    script = ''
      flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    '';
  };

  security = {
    rtkit = {
      enable = true;
    };
  };

  # Enable touchpad support (enabled default in most desktopManager).
  # services.xserver.libinput.enable = true;

  # Enable NoiseTorch with proper capabilities
  programs.noisetorch.enable = true;

  environment = {
    systemPackages = with pkgs; [
      brave
      git
      openssh
      xdg-user-dirs-gtk # This helps with Nautilus integration
      cachix
    ];

    # Set up my user icon
    etc = {
      "avatars/cartier.png".source = "${assets}/user-icon.png";
    };
  };

  users.users.cartier = {
    isNormalUser = true;
    description = "cartier";
    shell = pkgs.zsh;
    useDefaultShell = true;
    extraGroups = [
      "networkmanager"
      "wheel"
      "docker"
    ];

    #Virtualisation
    virtualisation.docker.enable = true;
  };

  system = {
    stateVersion = "25.05"; # Did you read the comment?
    activationScripts.avatar = ''
      mkdir -p /var/lib/AccountsService/icons
      ln -sf /etc/avatars/cartier.png /var/lib/AccountsService/icons/cartier
    '';
  };

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  nix.settings = {
    download-buffer-size = 134217728;
    http2 = false;
    substituters = [
      "https://cache.nixos.org/"
      "https://nix-community.cachix.org"
    ];
    trusted-public-keys = [
      "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
    ];
  };

  programs = {
    hyprland.enable = true;

    ssh = {
      startAgent = true;
      extraConfig = "
      Host myhost
        Hostname gitgud.foo 
    ";
    };

    # More thunar support
    xfconf = {
      enable = true;

    };

    zsh.enable = true;
  };

  nix.settings.experimental-features = [
    "nix-command"
    "flakes"
  ];

  # Theme
  stylix = {
    enable = true;
    base16Scheme = "${pkgs.base16-schemes}/share/themes/gruvbox-dark.yaml";
    # image = "/home/cartier/Documents/wallpapers/Fantasy-Mountain.png";
    polarity = "dark";
  };

  # Enable home manager
  home-manager = {
    useGlobalPkgs = true;
    extraSpecialArgs = {
      inherit inputs;
      assets = assets;
    };
    users = {
      "cartier" = {
        imports = [
          ../modules/home/home.nix
        ];
      };
    };
  };
}
