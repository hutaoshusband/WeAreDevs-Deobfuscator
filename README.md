# FireflyProtector Website

Official website for FireflyProtector - Advanced Application Security Solution.

## Features

- 🔐 **Secure Architecture**: Flat structure with `.htaccess` protection
- 🎨 **Modern Design**: Dark mode with glassmorphism and gradients
- 📱 **Responsive**: Mobile-first design
- 📖 **Documentation**: Integrated user guide with Markdown support
- ⚠️ **Error Reference**: Interactive error code table with search and filtering
- 💬 **Support Integration**: Discord community integration

## Installation

### Prerequisites

- PHP 7.4 or higher
- Apache with `mod_rewrite` enabled
- Composer

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/FireflyProtector-Website.git
cd FireflyProtector-Website
```

2. Install dependencies:
```bash
composer install
```

3. Copy `.env.example` to `.env` and configure:
```bash
copy .env.example .env
```

4. Edit `.env` with your settings:
```
APP_DEBUG=false
DISCORD_INVITE_URL=https://discord.com/invite/dUCNKkS2Ve
```

5. Ensure Apache has `AllowOverride All` for `.htaccess`:
```apache
<Directory "/var/www/fireflyprotector">
    AllowOverride All
</Directory>
```

6. Point your domain to the root directory (not to a `public` folder).

## Security Testing

After installation, verify security is working:

```bash
# Should work (200 OK)
curl http://yoursite.xyz/
curl http://yoursite.xyz/assets/css/style.css

# Should be blocked (403 Forbidden)
curl http://yoursite.xyz/.env
curl http://yoursite.xyz/app/Controllers/HomeController.php
curl http://yoursite.xyz/storage/docs/user-guide.md
curl http://yoursite.xyz/vendor/autoload.php
```

## Directory Structure

```
/
├── .htaccess           # Security rules & routing
├── .env               # Environment configuration (DO NOT COMMIT)
├── index.php          # Entry point
├── composer.json      # Dependencies
├── /app               # Application code (PROTECTED)
│   ├── /Controllers
│   ├── /Core
│   ├── /Config
│   └── /Views
├── /assets            # Public files (CSS, images)
│   ├── /css
│   └── /img
├── /storage           # Protected storage
│   └── /docs
└── /vendor            # Composer dependencies (PROTECTED)
```

## Routes

- `/` - Homepage
- `/about` - About page
- `/docs` - Documentation overview
- `/docs/user-guide` - User guide
- `/docs/error-codes` - Error codes reference
- `/support` - Support page

## Development

The application uses a simple MVC architecture:

- **Controllers**: Handle requests in `/app/Controllers`
- **Views**: Template files in `/app/Views`
- **Router**: Simple routing in `/app/Core/Router.php`
- **Routes**: Defined in `/app/Config/routes.php`

## Contributing

Contributions are welcome! Please ensure:

1. All sensitive directories remain protected by `.htaccess`
2. New routes are added to `/app/Config/routes.php`
3. CSS follows the existing design system
4. Code follows PSR-4 autoloading standards

## License

Proprietary - All rights reserved.

## Support

Join our Discord: [https://discord.com/invite/dUCNKkS2Ve](https://discord.com/invite/dUCNKkS2Ve)

**Note:** Active development and support have continued on GitHub. Please feel free to contribute or report issues by opening a ticket in the repository. The official website remains available for documentation and community resources.
