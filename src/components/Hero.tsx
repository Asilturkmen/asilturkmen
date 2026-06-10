import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Mail, FolderOpen, Github, Linkedin, Instagram } from 'lucide-react';
import profilePic from '../img/profile.png';
import { translations, Language } from '../data/translations';

interface HeroProps {
    language: Language;
}

const Hero = ({ language }: HeroProps) => {
    const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });
    const t = translations[language].hero;

    return (
        <section
            id="home"
            ref={ref}
            className="min-h-screen flex items-center justify-center relative overflow-hidden pt-20 md:pt-0"
        >
            {/* Subtle gradient background */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-transparent to-slate-900/40" />

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
                            className="text-lg text-blue-200 font-medium mb-4"
                            initial={{ opacity: 0 }}
                            animate={inView ? { opacity: 1 } : {}}
                            transition={{ delay: 0.2 }}
                        >
                            {t.greeting}
                        </motion.p>

                        <motion.h1
                            className="text-4xl md:text-5xl lg:text-7xl font-bold mb-4 sm:mb-6"
                            initial={{ opacity: 0 }}
                            animate={inView ? { opacity: 1 } : {}}
                            transition={{ delay: 0.3 }}
                        >
                            <span className="gradient-text">Asil Türkmen</span>
                        </motion.h1>

                        {/* Terminal Styled Role — centered on small screens, left from lg to match desktop column */}
                        <motion.div
                            className="text-base sm:text-lg md:text-xl lg:text-2xl mb-6 sm:mb-8 font-mono w-full flex justify-center lg:justify-start"
                            initial={{ opacity: 0 }}
                            animate={inView ? { opacity: 1 } : {}}
                            transition={{ delay: 0.4 }}
                        >
                            <div className="inline-block w-fit max-w-full text-left">
                                <div className="flex items-center gap-2 mb-1 text-slate-400">
                                    <span className="text-green-400">$</span>
                                    <span className="text-slate-300">whoami</span>
                                </div>
                                <div className="flex items-start gap-2">
                                    <span className="text-blue-400 shrink-0">&gt;</span>
                                    <div className="text-slate-300 min-w-0">
                                        {t.role}
                                        <br />
                                        <div className="flex items-center gap-2 flex-wrap mt-1">
                                            <span className="text-blue-200 break-words">{t.university}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            className="flex flex-col sm:flex-row flex-wrap gap-2 sm:gap-3 md:gap-4 justify-center lg:justify-start mb-8 sm:mb-12"
                            initial={{ opacity: 0 }}
                            animate={inView ? { opacity: 1 } : {}}
                            transition={{ delay: 0.5 }}
                        >
                            <button
                                onClick={() => document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })}
                                className="btn-primary w-full sm:w-auto max-sm:max-w-[220px] max-sm:mx-auto max-sm:py-2.5 max-sm:px-5 max-sm:text-sm max-sm:min-h-10 max-sm:font-semibold"
                            >
                                <Mail className="w-4 h-4 sm:w-5 sm:h-5 shrink-0" />
                                {t.cta1}
                            </button>

                            <button
                                onClick={() => document.getElementById('projects')?.scrollIntoView({ behavior: 'smooth' })}
                                className="btn-secondary w-full sm:w-auto max-sm:max-w-[220px] max-sm:mx-auto max-sm:py-2.5 max-sm:px-5 max-sm:text-sm max-sm:min-h-10 max-sm:font-semibold max-sm:border-[1.5px]"
                            >
                                <FolderOpen className="w-4 h-4 sm:w-5 sm:h-5 shrink-0" />
                                {t.cta2}
                            </button>
                        </motion.div>

                        <motion.div
                            className="flex gap-4 justify-center lg:justify-start"
                            initial={{ opacity: 0 }}
                            animate={inView ? { opacity: 1 } : {}}
                            transition={{ delay: 0.6 }}
                        >
                            <a href="https://github.com/Sonasil" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="GitHub profili">
                                <Github className="w-5 h-5" />
                            </a>
                            <a href="https://www.linkedin.com/in/asil-t%C3%BCrkmen-224ab0241/" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="LinkedIn profili">
                                <Linkedin className="w-5 h-5" />
                            </a>
                            <a href="https://www.instagram.com/asil_turkmen28/" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="Instagram profili">
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
                        <div className="relative w-64 h-64 md:w-80 md:h-80 lg:w-96 lg:h-96 mx-auto">
                            {/* Gradient glow effect */}
                            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 via-blue-600 to-blue-400 opacity-20 blur-3xl" />

                            {/* Profile image */}
                            <img
                                src={profilePic}
                                alt="Asil Türkmen"
                                className="relative z-10 rounded-full border-4 border-blue-500/40"
                            />
                        </div>
                    </motion.div>

                </div>
            </div>
        </section>
    );
};

export default Hero;
