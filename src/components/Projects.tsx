import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Github, ExternalLink } from 'lucide-react';
import yaylaHero from '../img/yayla-hero.jpg';
import test2DriveHero from '../img/test2drive-hero.png';
import hesappcimHero from '../img/hesappcim-hero.png';
import { translations, Language } from '../data/translations';

interface ProjectsProps {
    language: Language;
}

const Projects = ({ language }: ProjectsProps) => {
    const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });
    const t = translations[language].projects;

    const projects = [
        {
            title: t.project1.title,
            description: t.project1.description,
            tags: ['React', 'TypeScript', 'Tailwind CSS', 'Vercel'],
            image: hesappcimHero,
            github: 'https://github.com/Sonasil/HesAppcim',
            demo: 'https://hes-appcim.vercel.app'
        },
        {
            title: 'Test2Drive',
            description: t.project2.description,
            tags: ['Vue 3', 'Pinia', 'Vite', 'TypeScript'],
            image: test2DriveHero,
            github: 'https://github.com/Sonasil/TRAF101',
            demo: 'https://traf-101.vercel.app/'
        },
        {
            title: t.project3.title,
            description: t.project3.description,
            tags: ['React', 'TypeScript', 'Tailwind CSS', 'Vite'],
            image: yaylaHero,
            github: 'https://github.com/Sonasil/Yaylayemekevi',
            demo: 'https://yaylayemekevi.com'
        }
    ];

    return (
        <section
            id="projects"
            ref={ref}
            className="section-padding bg-slate-900/50"
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

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
                    {projects.map((project, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 30 }}
                            animate={inView ? { opacity: 1, y: 0 } : {}}
                            transition={{ duration: 0.6, delay: idx * 0.1 }}
                            className="card group flex flex-col"
                        >
                            {/* Project Image */}
                            <div className="relative overflow-hidden rounded-lg mb-4 aspect-video">
                                <img
                                    src={project.image}
                                    alt={project.title}
                                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/50 to-transparent opacity-60" />
                            </div>

                            {/* Project Info */}
                            <div className="flex-grow">
                                <h3 className="text-xl font-bold mb-3 text-white">{project.title}</h3>
                                <p className="text-sm md:text-base text-slate-400 mb-4 leading-relaxed">{project.description}</p>
                            </div>

                            {/* Tags */}
                            <div className="flex flex-wrap gap-2 mb-4">
                                {project.tags.map((tag, tagIdx) => (
                                    <span
                                        key={tagIdx}
                                        className="px-3 py-1 text-xs font-medium bg-amber-500/20 text-amber-300 rounded-full"
                                    >
                                        {tag}
                                    </span>
                                ))}
                            </div>

                            {/* Links */}
                            <div className="flex gap-3">
                                <a
                                    href={project.github}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:text-amber-400 transition-colors rounded-lg hover:bg-amber-500/10"
                                >
                                    <Github className="w-4 h-4" />
                                    {t.code}
                                </a>
                                <a
                                    href={project.demo}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:text-orange-400 transition-colors rounded-lg hover:bg-orange-500/10"
                                >
                                    <ExternalLink className="w-4 h-4" />
                                    {t.visit}
                                </a>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Projects;
