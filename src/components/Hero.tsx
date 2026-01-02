import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Mail, Eye, Github, Linkedin, Instagram, X, Download } from 'lucide-react';
import profilePic from '../img/profile.png';
import { translations, Language } from '../data/translations';

interface HeroProps {
    language: Language;
}

const Hero = ({ language }: HeroProps) => {
    const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });
    const [isCVOpen, setIsCVOpen] = useState(false);
    const t = translations[language].hero;

    return (
        <section
            id="home"
            ref={ref}
            className="min-h-screen flex items-center justify-center relative overflow-hidden pt-20 md:pt-0"
        >
            {/* Subtle gradient background */}
            <div className="absolute inset-0 bg-gradient-to-br from-amber-900/10 via-transparent to-orange-900/10" />

            <div className="container-custom relative z-10">
                <div className="grid lg:grid-cols-2 gap-12 items-center">

                    {/* Text Content */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={inView ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6 }}
                        className="text-center lg:text-left"
                    >
                        <motion.p
                            className="text-lg text-amber-400 font-medium mb-4"
                            initial={{ opacity: 0 }}
                            animate={inView ? { opacity: 1 } : {}}
                            transition={{ delay: 0.2 }}
                        >
                            {t.greeting}
                        </motion.p>

                        <motion.h1
                            className="text-5xl lg:text-7xl font-bold mb-6"
                            initial={{ opacity: 0 }}
                            animate={inView ? { opacity: 1 } : {}}
                            transition={{ delay: 0.3 }}
                        >
                            <span className="gradient-text">Asil Türkmen</span>
                        </motion.h1>

                        {/* Terminal Styled Role */}
                        <motion.div
                            className="text-xl lg:text-2xl mb-8 font-mono"
                            initial={{ opacity: 0 }}
                            animate={inView ? { opacity: 1 } : {}}
                            transition={{ delay: 0.4 }}
                        >
                            <div className="flex items-center gap-2 mb-1 text-slate-400">
                                <span className="text-green-400">$</span>
                                <span className="text-slate-300">whoami</span>
                            </div>
                            <div className="flex items-start gap-2">
                                <span className="text-amber-400">&gt;</span>
                                <div className="text-slate-300">
                                    {t.role}
                                    <br />
                                    <div className="flex items-center gap-2 flex-wrap mt-1">
                                        <span className="text-amber-400">{t.university}</span>
                                        <span className="text-xs px-2 py-0.5 bg-amber-500/10 text-amber-400/80 rounded border border-amber-500/20 font-mono">
                                            #F59E0B
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            className="flex flex-wrap gap-4 justify-center lg:justify-start mb-8"
                            initial={{ opacity: 0 }}
                            animate={inView ? { opacity: 1 } : {}}
                            transition={{ delay: 0.5 }}
                        >
                            <button
                                onClick={() => document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })}
                                className="btn-primary"
                            >
                                <Mail className="w-5 h-5" />
                                {t.cta1}
                            </button>

                            <button
                                onClick={() => setIsCVOpen(true)}
                                className="btn-secondary"
                            >
                                <Eye className="w-5 h-5" />
                                {t.cta2}
                            </button>
                        </motion.div>

                        <motion.div
                            className="flex gap-4 justify-center lg:justify-start"
                            initial={{ opacity: 0 }}
                            animate={inView ? { opacity: 1 } : {}}
                            transition={{ delay: 0.6 }}
                        >
                            <a href="https://github.com/Sonasil" target="_blank" rel="noopener noreferrer" className="social-icon">
                                <Github className="w-5 h-5" />
                            </a>
                            <a href="https://www.linkedin.com/in/asil-t%C3%BCrkmen-224ab0241/" target="_blank" rel="noopener noreferrer" className="social-icon">
                                <Linkedin className="w-5 h-5" />
                            </a>
                            <a href="https://www.instagram.com/asil_turkmen28/" target="_blank" rel="noopener noreferrer" className="social-icon">
                                <Instagram className="w-5 h-5" />
                            </a>
                        </motion.div>
                    </motion.div>

                    {/* Profile Image with Floating Binary Particles */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={inView ? { opacity: 1, scale: 1 } : {}}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="relative"
                    >
                        <div className="relative w-72 h-72 lg:w-96 lg:h-96 mx-auto">
                            {/* Gradient glow effect */}
                            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-amber-500 via-orange-500 to-pink-500 opacity-20 blur-3xl" />

                            {/* Profile image */}
                            <img
                                src={profilePic}
                                alt="Asil Türkmen"
                                className="relative z-10 rounded-full border-4 border-amber-500/30"
                            />
                        </div>
                    </motion.div>

                </div>
            </div>

            {/* CV Modal */}
            <AnimatePresence>
                {isCVOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
                        onClick={() => setIsCVOpen(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-5xl h-[85vh] flex flex-col shadow-2xl overflow-hidden"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {/* Modal Header */}
                            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700 bg-slate-800/50">
                                <h3 className="text-xl font-bold text-slate-200">
                                    {language === 'en' ? 'CV Preview' : 'CV Önizleme'}
                                </h3>
                                <div className="flex items-center gap-3">
                                    <a
                                        href="/Englishcv.pdf"
                                        download="Asil_Turkmen_CV.pdf"
                                        className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 rounded-lg transition-colors border border-amber-500/20"
                                    >
                                        <Download className="w-4 h-4" />
                                        {language === 'en' ? 'Download' : 'İndir'}
                                    </a>
                                    <button
                                        onClick={() => setIsCVOpen(false)}
                                        className="p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
                                    >
                                        <X className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>

                            {/* PDF Viewer */}
                            <div className="flex-1 bg-slate-800 overflow-hidden relative">
                                <iframe
                                    src="/Englishcv.pdf"
                                    className="w-full h-full"
                                    title="CV Preview"
                                />

                                {/* Fallback for mobile or if nice PDF viewing fails */}
                                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 md:hidden">
                                    <a
                                        href="/Englishcv.pdf"
                                        target="_blank"
                                        className="px-6 py-3 bg-amber-600 text-white rounded-full shadow-lg font-bold"
                                    >
                                        {language === 'en' ? 'Open PDF' : 'PDF\'i Aç'}
                                    </a>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </section>
    );
};

export default Hero;
