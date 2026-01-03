import { Github, Linkedin, Instagram } from 'lucide-react';
import { translations, Language } from '../data/translations';

interface FooterProps {
    language: Language;
}

const Footer = ({ language }: FooterProps) => {
    const t = translations[language].contact;

    return (
        <footer className="pt-12 md:pt-16 pb-8 bg-slate-950/50 border-t border-slate-800">
            <div className="container-custom">
                <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-slate-400">
                        {t.footer}
                    </p>

                    <div className="flex gap-4">
                        <a href="https://github.com/Sonasil" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-amber-400 transition-colors">
                            <Github className="w-5 h-5" />
                        </a>
                        <a href="https://www.linkedin.com/in/asil-t%C3%BCrkmen-224ab0241/" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-orange-400 transition-colors">
                            <Linkedin className="w-5 h-5" />
                        </a>
                        <a href="https://www.instagram.com/asil_turkmen28/" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-pink-400 transition-colors">
                            <Instagram className="w-5 h-5" />
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
