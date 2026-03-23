import { useEffect, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Github, ExternalLink, Search, ArrowUpRight } from 'lucide-react';
import yaylaHero from '../img/yayla-hero.jpg';
import test2DriveHero from '../img/test2drive-hero.png';
import hesappcimHero from '../img/hesappcim-hero.png';
import nedirBeoHero from '../img/NedirBeo.png';
import { translations, Language } from '../data/translations';

interface ProjectsProps {
    language: Language;
}

const Projects = ({ language }: ProjectsProps) => {
    const t = translations[language].projects;
    const [searchQuery, setSearchQuery] = useState('');

    const projects = [
        {
            id: 1,
            title: t.project4.title,
            domain: 'Community / Dictionary Platform',
            year: '2026',
            description: t.project4.description,
            tags: ['React', 'TypeScript', 'Vite', 'Node.js', 'Express'],
            image: nedirBeoHero,
            github: 'https://github.com/Sonasil/NedirBeo.git',
            demo: 'https://github.com/Sonasil/NedirBeo.git'
        },
        {
            id: 2,
            title: t.project1.title,
            domain: 'Finance / Productivity',
            year: '2025',
            description: t.project1.description,
            tags: ['React', 'TypeScript', 'Tailwind CSS', 'Vercel'],
            image: hesappcimHero,
            github: 'https://github.com/Sonasil/HesAppcim',
            demo: 'https://hes-appcim.vercel.app'
        },
        {
            id: 3,
            title: 'Test2Drive',
            domain: 'Education / Mobility',
            year: '2024',
            description: t.project2.description,
            tags: ['Vue 3', 'Pinia', 'Vite', 'TypeScript'],
            image: test2DriveHero,
            github: 'https://github.com/Sonasil/TRAF101',
            demo: 'https://traf-101.vercel.app/'
        },
        {
            id: 4,
            title: t.project3.title,
            domain: 'Restaurant / Showcase',
            year: '2023',
            description: t.project3.description,
            tags: ['React', 'TypeScript', 'Tailwind CSS', 'Vite'],
            image: yaylaHero,
            github: 'https://github.com/Sonasil/Yaylayemekevi',
            demo: 'https://yaylayemekevi.com'
        }
    ];

    const filteredAndSortedProjects = useMemo(() => {
        let result = [...projects];

        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            result = result.filter(
                (project) =>
                    project.title.toLowerCase().includes(query) ||
                    project.domain.toLowerCase().includes(query) ||
                    project.tags.some((tag) => tag.toLowerCase().includes(query))
            );
        }

        return result;
    }, [projects, searchQuery]);

    const [selectedProject, setSelectedProject] = useState(projects[0]);
    const [expandedProjectId, setExpandedProjectId] = useState<number | null>(projects[0].id);

    useEffect(() => {
        if (filteredAndSortedProjects.length === 0) {
            return;
        }

        const isSelectedVisible = filteredAndSortedProjects.some(
            (project) => project.id === selectedProject.id
        );

        if (!isSelectedVisible) {
            setSelectedProject(filteredAndSortedProjects[0]);
            setExpandedProjectId(filteredAndSortedProjects[0].id);
        }
    }, [filteredAndSortedProjects, selectedProject.id]);

    return (
        <section id="projects" className="min-h-screen py-16 md:py-20 px-4 md:px-8 lg:px-16 max-w-[1600px] mx-auto">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-12 md:mb-24">
                <div>
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tighter text-slate-100"
                    >
                        {t.title}
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-slate-400 mt-4 text-base md:text-xl max-w-md"
                    >
                        {t.subtitle}
                    </motion.p>
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="flex flex-col sm:flex-row gap-3 w-full md:w-auto"
                >
                    <div className="relative w-full sm:w-64 lg:w-80">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input
                            type="text"
                            placeholder={t.searchPlaceholder}
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-slate-900/50 border border-slate-800 text-slate-100 rounded-full pl-11 pr-4 py-3 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-slate-600"
                        />
                    </div>

                </motion.div>
            </div>

            <div className="flex flex-col lg:flex-row gap-12 lg:gap-24 relative">
                <div className="w-full lg:w-1/2 flex flex-col border-t border-slate-800">
                    {filteredAndSortedProjects.map((project, index) => {
                        const isExpanded = expandedProjectId === project.id;
                        const isSelected = selectedProject.id === project.id;

                        return (
                            <motion.div
                                key={project.id}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: Math.min(index * 0.05, 0.5) }}
                                onClick={() => {
                                    setExpandedProjectId(isExpanded ? null : project.id);
                                    setSelectedProject(project);
                                }}
                                className={`group flex flex-col py-6 md:py-8 border-b transition-colors duration-300 cursor-pointer ${isSelected ? 'border-blue-500/50' : 'border-slate-800 hover:border-slate-500'}`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex flex-col gap-2">
                                        <h3 className={`text-2xl md:text-4xl font-bold transition-colors duration-300 ${isExpanded || isSelected ? 'text-blue-400' : 'text-slate-300 group-hover:text-slate-100'}`}>
                                            {project.title}
                                        </h3>
                                        <div className={`flex flex-wrap items-center gap-2 md:gap-3 text-xs md:text-base transition-colors duration-300 ${isExpanded || isSelected ? 'text-slate-300' : 'text-slate-500 group-hover:text-slate-400'}`}>
                                            <span className="font-mono text-blue-500/80">{project.year}</span>
                                            <span className="w-1 h-1 rounded-full bg-slate-700"></span>
                                            <span>{project.domain}</span>
                                            <span className="w-1 h-1 rounded-full bg-slate-700 hidden sm:block"></span>
                                            <span className="hidden sm:block">{project.tags.join(' • ')}</span>
                                        </div>
                                    </div>

                                    <div className={`transition-transform duration-500 ${isExpanded ? 'rotate-45 text-blue-400' : isSelected ? 'text-blue-400' : 'text-slate-600 group-hover:text-slate-300 group-hover:-translate-y-1 group-hover:translate-x-1'}`}>
                                        <ArrowUpRight className="w-6 h-6 md:w-8 md:h-8" />
                                    </div>
                                </div>

                                <AnimatePresence>
                                    {isExpanded && (
                                        <motion.div
                                            initial={{ height: 0, opacity: 0 }}
                                            animate={{ height: 'auto', opacity: 1 }}
                                            exit={{ height: 0, opacity: 0 }}
                                            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                                            className="overflow-hidden"
                                        >
                                            <div className="pt-6 pb-2">
                                                <div className="rounded-2xl border border-slate-800/90 bg-slate-900/40 p-5 md:p-6">
                                                    <p className="text-sm md:text-base text-slate-200 leading-7 mb-5">
                                                        {project.description}
                                                    </p>

                                                    <div className="flex flex-wrap gap-2 mb-5">
                                                        {project.tags.map((tag) => (
                                                            <span
                                                                key={tag}
                                                                className="px-3 py-1.5 bg-blue-500/10 rounded-full text-xs font-medium text-blue-200 border border-blue-500/20"
                                                            >
                                                                {tag}
                                                            </span>
                                                        ))}
                                                    </div>

                                                    <div className="flex flex-col sm:flex-row gap-3">
                                                        <a
                                                            href={project.demo}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            onClick={(e) => e.stopPropagation()}
                                                            className="flex-1 bg-blue-600 text-white py-3.5 rounded-xl font-semibold flex justify-center items-center gap-2 active:scale-95 transition-all shadow-lg shadow-blue-900/20 hover:bg-blue-500"
                                                        >
                                                            <ExternalLink className="w-4 h-4" /> {t.visit}
                                                        </a>
                                                        <a
                                                            href={project.github}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            onClick={(e) => e.stopPropagation()}
                                                            className="flex-1 bg-slate-800 text-slate-100 py-3.5 rounded-xl font-semibold flex justify-center items-center gap-2 active:scale-95 transition-all border border-slate-700 shadow-lg hover:bg-slate-700 hover:border-slate-600"
                                                        >
                                                            <Github className="w-4 h-4" /> {t.code}
                                                        </a>
                                                    </div>
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </motion.div>
                        );
                    })}

                    {filteredAndSortedProjects.length === 0 && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="py-20 text-center flex flex-col items-center justify-center gap-4"
                        >
                            <div className="w-16 h-16 rounded-full bg-slate-900 flex items-center justify-center">
                                <Search className="w-6 h-6 text-slate-600" />
                            </div>
                            <p className="text-slate-400 text-lg">
                                {t.noProjectsFound.replace('{query}', searchQuery)}
                            </p>
                            <button
                                onClick={() => setSearchQuery('')}
                                className="text-blue-400 underline underline-offset-4 hover:text-blue-300 transition-colors"
                            >
                                {t.clearSearch}
                            </button>
                        </motion.div>
                    )}
                </div>

                <div className="hidden lg:block w-1/2 relative">
                    <div className="sticky top-24 h-[600px] w-full rounded-3xl overflow-hidden bg-slate-900 border border-slate-800 shadow-2xl shadow-blue-900/10">
                        <AnimatePresence mode="wait">
                            {filteredAndSortedProjects.length > 0 ? (
                                <motion.div
                                    key={selectedProject.id}
                                    initial={{ opacity: 0, scale: 1.05 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0 }}
                                    transition={{ duration: 0.4, ease: 'easeInOut' }}
                                    className="absolute inset-0"
                                >
                                    <img
                                        src={selectedProject.image}
                                        alt={selectedProject.title}
                                        className="w-full h-full object-cover"
                                    />

                                    <div className="absolute bottom-10 left-10 right-10 flex justify-between items-end gap-4">
                                        <div>
                                            <motion.h3
                                                initial={{ y: 20, opacity: 0 }}
                                                animate={{ y: 0, opacity: 1 }}
                                                transition={{ delay: 0.1 }}
                                                className="text-4xl font-bold text-white mb-3"
                                            >
                                                {selectedProject.title}
                                            </motion.h3>
                                            <motion.div
                                                initial={{ y: 20, opacity: 0 }}
                                                animate={{ y: 0, opacity: 1 }}
                                                transition={{ delay: 0.15 }}
                                                className="flex flex-wrap gap-2"
                                            >
                                                {selectedProject.tags.map((tag) => (
                                                    <span key={tag} className="px-3 py-1.5 bg-blue-500/20 backdrop-blur-md rounded-full text-xs font-medium text-blue-100 border border-blue-500/30 shadow-sm">
                                                        {tag}
                                                    </span>
                                                ))}
                                            </motion.div>
                                        </div>
                                        <motion.div
                                            initial={{ x: 20, opacity: 0 }}
                                            animate={{ x: 0, opacity: 1 }}
                                            transition={{ delay: 0.3 }}
                                            className="flex gap-3"
                                        >
                                            <a
                                                href={selectedProject.demo}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="w-14 h-14 rounded-full bg-blue-600 text-white flex items-center justify-center hover:scale-110 hover:bg-blue-500 transition-all shadow-xl shadow-blue-900/20"
                                                aria-label={t.visit}
                                            >
                                                <ExternalLink className="w-6 h-6" />
                                            </a>
                                            <a
                                                href={selectedProject.github}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="w-14 h-14 rounded-full bg-slate-800/80 backdrop-blur-md text-white border border-slate-700 flex items-center justify-center hover:bg-slate-700 transition-colors shadow-xl"
                                                aria-label={t.code}
                                            >
                                                <Github className="w-6 h-6" />
                                            </a>
                                        </motion.div>
                                    </div>
                                </motion.div>
                            ) : (
                                <div className="absolute inset-0 flex items-center justify-center bg-slate-900">
                                    <span className="text-slate-600">{t.noPreview}</span>
                                </div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Projects;
