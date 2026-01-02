import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Languages } from 'lucide-react';
import { Language } from '../data/translations';

interface NavbarProps {
    language: Language;
    toggleLanguage: () => void;
}

const Navbar = ({ language, toggleLanguage }: NavbarProps) => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navLinks = [
        { name: language === 'en' ? 'Home' : 'Ana Sayfa', href: '#home' },
        { name: language === 'en' ? 'About' : 'Hakkımda', href: '#about' },
        { name: language === 'en' ? 'Skills' : 'Yetenekler', href: '#skills' },
        { name: language === 'en' ? 'Projects' : 'Projeler', href: '#projects' },
        { name: language === 'en' ? 'Contact' : 'İletişim', href: '#contact' },
    ];

    const handleScrollTo = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
        e.preventDefault();
        const element = document.querySelector(href);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
            setIsMobileMenuOpen(false);
        }
    };

    return (
        <nav
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled ? 'bg-slate-900/90 backdrop-blur-md shadow-lg py-4' : 'bg-transparent py-6'
                }`}
        >
            <div className="container-custom flex justify-between items-center">
                {/* Logo */}
                <a
                    href="#home"
                    onClick={(e) => handleScrollTo(e, '#home')}
                    className="text-2xl font-bold gradient-text"
                >
                    Asil Türkmen
                </a>

                {/* Desktop Menu */}
                <div className="hidden md:flex items-center gap-8">
                    {navLinks.map((link) => (
                        <a
                            key={link.name}
                            href={link.href}
                            onClick={(e) => handleScrollTo(e, link.href)}
                            className="text-sm font-medium text-slate-300 hover:text-amber-400 transition-colors"
                        >
                            {link.name}
                        </a>
                    ))}

                    {/* Language Toggle */}
                    <button
                        onClick={toggleLanguage}
                        className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/50 border border-slate-700/50 hover:border-amber-500/50 rounded-full text-slate-200 hover:text-amber-400 transition-all duration-300"
                    >
                        <Languages className="w-4 h-4" />
                        <span className="text-xs font-bold">{language === 'en' ? 'TR' : 'EN'}</span>
                    </button>
                </div>

                {/* Mobile Menu Button */}
                <button
                    className="md:hidden text-slate-200"
                    onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                >
                    {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
            </div>

            {/* Mobile Menu Overlay */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="md:hidden bg-slate-900/95 backdrop-blur-lg border-t border-slate-800"
                    >
                        <div className="container-custom py-6 flex flex-col gap-4">
                            {navLinks.map((link) => (
                                <a
                                    key={link.name}
                                    href={link.href}
                                    onClick={(e) => handleScrollTo(e, link.href)}
                                    className="text-lg font-medium text-slate-300 hover:text-amber-400 transition-colors py-2"
                                >
                                    {link.name}
                                </a>
                            ))}

                            <div className="pt-4 border-t border-slate-800 mt-2">
                                <button
                                    onClick={toggleLanguage}
                                    className="flex items-center gap-2 text-slate-300 hover:text-amber-400"
                                >
                                    <Languages className="w-5 h-5" />
                                    <span>{language === 'en' ? 'Switch to Turkish' : 'İngilizceye Geç'}</span>
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
};

export default Navbar;
