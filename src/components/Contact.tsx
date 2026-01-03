import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Send } from 'lucide-react';
import toast from 'react-hot-toast';
import { translations, Language } from '../data/translations';

interface ContactProps {
    language: Language;
}

const Contact = ({ language }: ContactProps) => {
    const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });
    const t = translations[language].contact;

    const [formData, setFormData] = useState({
        name: '',
        email: '',
        message: ''
    });

    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        const formDataToSend = {
            access_key: "856f7b76-916d-4768-ae34-020e0f6052fc",
            name: formData.name,
            email: formData.email,
            message: formData.message
        };

        try {
            const response = await fetch("https://api.web3forms.com/submit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formDataToSend)
            });

            const data = await response.json();

            if (data.success) {
                toast.success(t.success);
                setFormData({ name: '', email: '', message: '' });
            } else {
                toast.error(t.error);
            }
        } catch (error) {
            console.error("Error:", error);
            toast.error(t.generalError);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <section
            id="contact"
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

                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={inView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="max-w-2xl mx-auto px-4 sm:px-6"
                >
                    <form onSubmit={handleSubmit} className="space-y-6">

                        <div>
                            <label htmlFor="name" className="block text-sm font-medium text-slate-200 mb-2">
                                {t.name}
                            </label>
                            <input
                                type="text"
                                id="name"
                                required
                                className="input-field"
                                placeholder={t.namePlaceholder}
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            />
                        </div>

                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-slate-200 mb-2">
                                {t.email}
                            </label>
                            <input
                                type="email"
                                id="email"
                                required
                                className="input-field"
                                placeholder={t.emailPlaceholder}
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            />
                        </div>

                        <div>
                            <label htmlFor="message" className="block text-sm font-medium text-slate-200 mb-2">
                                {t.message}
                            </label>
                            <textarea
                                id="message"
                                rows={5}
                                required
                                className="input-field resize-none"
                                placeholder={t.messagePlaceholder}
                                value={formData.message}
                                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                            />
                        </div>

                        <button type="submit" className="btn-primary w-full justify-center" disabled={isSubmitting}>
                            <Send className="w-5 h-5" />
                            {isSubmitting ? t.sending : t.send}
                        </button>

                    </form>

                    {/* Contact Info */}
                    <div className="mt-12 text-center">
                        <p className="text-slate-400 mb-4">{t.or}</p>
                        <a
                            href="mailto:turkmenasil@hotmail.com"
                            className="text-amber-400 hover:text-amber-300 transition-colors font-medium"
                        >
                            turkmenasil@hotmail.com
                        </a>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};

export default Contact;
