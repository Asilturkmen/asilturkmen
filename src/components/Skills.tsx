import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Code2, Database, Wrench } from 'lucide-react';
import { translations, Language } from '../data/translations';

interface SkillsProps {
    language: Language;
}

const Skills = ({ language }: SkillsProps) => {
    const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });
    const t = translations[language].skills;

    const skillsData = {
        frontend: ['React', 'Vue 3', 'TypeScript', 'JavaScript', 'HTML5', 'CSS3', 'Tailwind CSS', 'Pinia', 'Responsive Design'],
        backend: ['Node.js', 'Python', 'Next.js', 'REST APIs', 'SQL'],
        tools: ['Git', 'GitHub', 'Vite', 'Vercel', 'VS Code', 'Figma']
    };

    return (
        <section
            id="skills"
            ref={ref}
            className="section-padding"
        >
            <div className="container-custom">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={inView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.6 }}
                    className="section-header"
                >
                    <h2 className="section-title gradient-text">{t.title}</h2>
                    <p className="section-subtitle">{t.subtitle}</p>
                </motion.div>

                <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">

                    {/* Frontend */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={inView ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="card"
                    >
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-amber-500/20 to-orange-500/20 flex items-center justify-center">
                                <Code2 className="w-6 h-6 text-amber-400" />
                            </div>
                            <h3 className="text-xl font-bold">{t.frontend}</h3>
                        </div>

                        <div className="flex flex-wrap gap-2">
                            {skillsData.frontend.map((skill, idx) => (
                                <span
                                    key={idx}
                                    className="px-3 py-1.5 text-sm font-medium bg-slate-800/50 hover:bg-amber-500/20 text-slate-200 hover:text-amber-300 rounded-lg transition-all duration-300 border border-slate-700/50 hover:border-amber-500/30"
                                >
                                    {skill}
                                </span>
                            ))}
                        </div>
                    </motion.div>

                    {/* Backend */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={inView ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="card"
                    >
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-orange-500/20 to-pink-500/20 flex items-center justify-center">
                                <Database className="w-6 h-6 text-orange-400" />
                            </div>
                            <h3 className="text-xl font-bold">{t.backend}</h3>
                        </div>

                        <div className="flex flex-wrap gap-2">
                            {skillsData.backend.map((skill, idx) => (
                                <span
                                    key={idx}
                                    className="px-3 py-1.5 text-sm font-medium bg-slate-800/50 hover:bg-orange-500/20 text-slate-200 hover:text-orange-300 rounded-lg transition-all duration-300 border border-slate-700/50 hover:border-orange-500/30"
                                >
                                    {skill}
                                </span>
                            ))}
                        </div>
                    </motion.div>

                    {/* Tools */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={inView ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="card"
                    >
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-pink-500/20 to-purple-500/20 flex items-center justify-center">
                                <Wrench className="w-6 h-6 text-pink-400" />
                            </div>
                            <h3 className="text-xl font-bold">{t.tools}</h3>
                        </div>

                        <div className="flex flex-wrap gap-2">
                            {skillsData.tools.map((skill, idx) => (
                                <span
                                    key={idx}
                                    className="px-3 py-1.5 text-sm font-medium bg-slate-800/50 hover:bg-pink-500/20 text-slate-200 hover:text-pink-300 rounded-lg transition-all duration-300 border border-slate-700/50 hover:border-pink-500/30"
                                >
                                    {skill}
                                </span>
                            ))}
                        </div>
                    </motion.div>

                </div>
            </div>
        </section>
    );
};

export default Skills;
