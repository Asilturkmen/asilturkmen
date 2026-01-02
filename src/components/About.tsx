import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { translations, Language } from '../data/translations';

interface AboutProps {
    language: Language;
}

const About = ({ language }: AboutProps) => {
    const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });
    const t = translations[language].about;

    return (
        <section
            id="about"
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

                <div className="max-w-4xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={inView ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="space-y-6 text-lg text-slate-300 leading-relaxed"
                    >
                        <p>{t.p1}</p>
                        <p>{t.p2}</p>
                        <p>{t.p3}</p>
                        <p>{t.p4}</p>
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default About;
