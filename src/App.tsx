import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import {
  Github,
  Instagram,
  Linkedin,
  Mail,
  Send,
  Download,
  ExternalLink,
  Code2,
  Database,
  Wrench,
  Languages
} from 'lucide-react';
import profilePic from './img/profile.png';
import yaylaHero from './img/yayla-hero.jpg';

function App() {
  const [language, setLanguage] = useState<'tr' | 'en'>('en');

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });

  // Intersection observers for sections
  const [heroRef, heroInView] = useInView({ triggerOnce: true, threshold: 0.1 });
  const [aboutRef, aboutInView] = useInView({ triggerOnce: true, threshold: 0.1 });
  const [skillsRef, skillsInView] = useInView({ triggerOnce: true, threshold: 0.1 });
  const [projectsRef, projectsInView] = useInView({ triggerOnce: true, threshold: 0.1 });
  const [contactRef, contactInView] = useInView({ triggerOnce: true, threshold: 0.1 });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const mailtoLink = `mailto:turkmenasil@hotmail.com?subject=Contact from ${formData.name}&body=Name: ${formData.name}%0D%0AEmail: ${formData.email}%0D%0AMessage: ${formData.message}`;
    window.location.href = mailtoLink;
  };

  const handleDownloadCV = () => {
    const link = document.createElement('a');
    link.href = '/Englishcv.pdf';
    link.download = 'Englishcv.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'en' ? 'tr' : 'en');
  };

  // Translations
  const translations = {
    tr: {
      hero: {
        greeting: 'Merhaba, Ben',
        role: 'Yazılım Mühendisliği Öğrencisi',
        university: 'Doğu Akdeniz Üniversitesi',
        cta1: 'İletişime Geç',
        cta2: 'CV İndir'
      },
      about: {
        title: 'Hakkımda',
        subtitle: 'Beni daha yakından tanıyın',
        p1: 'Ben Asil Türkmen. Doğu Akdeniz Üniversitesi\'nde Yazılım Mühendisliği öğrencisiyim. Web ve mobil uygulama projelerinde yer aldım ve bu alanlarda pratik deneyim kazandım.',
        p2: 'Yazılım geliştirirken benim için en önemli şey, yapılan işin gerçekten çalışıyor olması ve geliştirilebilir kalması. Öğrendiklerimi doğrudan projelere uygulamayı seviyorum; bu yüzden çoğunlukla deneye deneye ilerliyorum.',
        p3: 'Yeni şeyler öğrenmeye istekli, sorumluluk almaktan çekinmeyen biriyim. Mükemmel olduğumu iddia etmiyorum ama kendimi sürekli geliştirmeye önem veriyorum ve bu süreci ciddiye alıyorum.',
        p4: 'Şu anda gerçek projelerde yer alabileceğim, katkı sağlayıp aynı zamanda öğrenebileceğim staj veya junior seviye fırsatlar arıyorum.'
      },
      skills: {
        title: 'Yetenekler & Teknolojiler',
        subtitle: 'Çalıştığım teknolojiler',
        frontend: 'Frontend',
        backend: 'Backend',
        tools: 'Araçlar'
      },
      projects: {
        title: 'Öne Çıkan Projeler',
        subtitle: 'Son çalışmalarımdan bazıları',
        project1: {
          title: '💰 HesAppcım',
          description: 'Grup harcamalarını takip etmeyi ve borçları dengelemeyi kolaylaştıran modern uygulama. Akıllı hesaplama, otomatik denge, grup yönetimi ve Türkçe/İngilizce dil desteği ile tatil, ev ve buluşmalarınızda hesaplaşma sorununu çözer.'
        },
        project2: {
          title: '🚗 TRAF101',
          description: 'KKTC sürücü belgesi sınavlarına hazırlık için kapsamlı quiz uygulaması. 144+ trafik işareti, lisans türüne özel testler, ilerleme takibi ve çift dil desteği (TR/EN) ile modern Vue 3 ve Pinia kullanılarak geliştirilmiş.'
        },
        project3: {
          title: '🍽️ Yayla Yemek Evi',
          description: 'Kuzey Kıbrıs\'ta Pamuklu Köyü\'nde bulunan otantik köy restoranı için modern ve responsive web sitesi. İnteraktif galeri, Google Maps entegrasyonu, müşteri yorumları ve hızlı iletişim özellikleri ile doğal ürünler ve geleneksel lezzetleri dijital ortamda tanıtıyor.'
        },
        code: 'Kod',
        demo: 'Demo'
      },
      contact: {
        title: 'İletişime Geçin',
        subtitle: 'Birlikte çalışalım',
        name: 'İsim',
        email: 'E-posta',
        message: 'Mesaj',
        send: 'Mesaj Gönder',
        namePlaceholder: 'Adınız',
        emailPlaceholder: 'ornek@email.com',
        messagePlaceholder: 'Mesajınız...',
        or: 'Veya doğrudan bana ulaşın:',
        footer: '© 2024 Asil Türkmen. Tüm hakları saklıdır.'
      }
    },
    en: {
      hero: {
        greeting: 'Hi, I am',
        role: 'Software Engineering Student',
        university: 'Eastern Mediterranean University',
        cta1: 'Get In Touch',
        cta2: 'Download CV'
      },
      about: {
        title: 'About Me',
        subtitle: 'Get to know me better',
        p1: 'I\'m Asil Türkmen, a Software Engineering student at Eastern Mediterranean University. I have participated in web and mobile application projects, gaining practical experience in these areas.',
        p2: 'When developing software, what matters most to me is that the work actually functions and remains maintainable. I enjoy applying what I learn directly to projects, which is why I mostly progress through hands-on experimentation.',
        p3: 'I\'m eager to learn new things and not afraid to take responsibility. I don\'t claim to be perfect, but I value continuous self-improvement and take this process seriously.',
        p4: 'Currently, I\'m seeking internship or junior-level opportunities where I can contribute to real projects while continuing to learn and grow.'
      },
      skills: {
        title: 'Skills & Technologies',
        subtitle: 'Technologies I work with',
        frontend: 'Frontend',
        backend: 'Backend',
        tools: 'Tools'
      },
      projects: {
        title: 'Featured Projects',
        subtitle: 'Some of my recent work',
        project1: {
          title: '💰 HesAppcım',
          description: 'A modern expense tracking app that simplifies group spending and debt balancing. Features smart calculations, automatic balance tracking, group management, and bilingual support (TR/EN) for vacations, roommates, and gatherings.'
        },
        project2: {
          title: '🚗 TRAF101',
          description: 'Comprehensive TRNC/KKTC driving license exam preparation app. Features 144+ traffic signs, license-specific practice tests, progress tracking, and bilingual support (TR/EN). Built with modern Vue 3 and Pinia state management.'
        },
        project3: {
          title: '🍽️ Yayla Yemek Evi',
          description: 'Modern and responsive website for an authentic village restaurant in Pamuklu Village, North Cyprus. Features interactive gallery, Google Maps integration, customer reviews, and quick contact capabilities to showcase natural products and traditional flavors digitally.'
        },
        code: 'Code',
        demo: 'Demo'
      },
      contact: {
        title: 'Get In Touch',
        subtitle: 'Let\'s work together',
        name: 'Name',
        email: 'Email',
        message: 'Message',
        send: 'Send Message',
        namePlaceholder: 'Your Name',
        emailPlaceholder: 'your.email@example.com',
        messagePlaceholder: 'Your message...',
        or: 'Or reach me directly at:',
        footer: '© 2024 Asil Türkmen. All rights reserved.'
      }
    }
  };

  const t = translations[language];

  // Skills data - Professional badge style
  const skills = {
    frontend: ['React', 'TypeScript', 'JavaScript', 'HTML5', 'CSS3', 'Tailwind CSS', 'Responsive Design'],
    backend: ['Node.js', 'Python', 'SQL', 'REST APIs', 'Express.js'],
    tools: ['Git', 'GitHub', 'VS Code', 'Figma', 'npm', 'Vite']
  };

  // Projects data
  const projects = [
    {
      title: t.projects.project1.title,
      description: t.projects.project1.description,
      tags: ['React', 'TypeScript', 'Tailwind CSS', 'Vercel'],
      image: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&q=80&w=800',
      github: 'https://github.com/Sonasil/HesAppcim',
      demo: 'https://hes-appcim.vercel.app'
    },
    {
      title: t.projects.project2.title,
      description: t.projects.project2.description,
      tags: ['Vue 3', 'Pinia', 'Vite', 'TypeScript'],
      image: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&q=80&w=800',
      github: 'https://github.com/Sonasil/TRAF101',
      demo: 'https://github.com/Sonasil/TRAF101'
    },
    {
      title: t.projects.project3.title,
      description: t.projects.project3.description,
      tags: ['React', 'TypeScript', 'Tailwind CSS', 'Vite'],
      image: yaylaHero,
      github: 'https://github.com/Sonasil/Yaylayemekevi',
      demo: 'https://yaylayemekevi.vercel.app'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">

      {/* Language Toggle Button - Fixed Position */}
      <motion.button
        onClick={toggleLanguage}
        className="fixed top-6 right-6 z-50 flex items-center gap-2 px-4 py-2 bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 hover:border-amber-500/50 rounded-full text-slate-200 hover:text-amber-400 transition-all duration-300 shadow-lg hover:shadow-amber-500/20"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Languages className="w-4 h-4" />
        <span className="font-medium text-sm">{language === 'en' ? 'TR' : 'EN'}</span>
      </motion.button>

      {/* Hero Section */}
      <section
        ref={heroRef}
        className="min-h-screen flex items-center justify-center relative overflow-hidden"
      >
        {/* Subtle gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-amber-900/10 via-transparent to-orange-900/10" />

        <div className="container-custom relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">

            {/* Text Content */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={heroInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="text-center lg:text-left"
            >
              <motion.p
                className="text-lg text-amber-400 font-medium mb-4"
                initial={{ opacity: 0 }}
                animate={heroInView ? { opacity: 1 } : {}}
                transition={{ delay: 0.2 }}
              >
                {t.hero.greeting}
              </motion.p>

              <motion.h1
                className="text-5xl lg:text-7xl font-bold mb-6"
                initial={{ opacity: 0 }}
                animate={heroInView ? { opacity: 1 } : {}}
                transition={{ delay: 0.3 }}
              >
                <span className="gradient-text">Asil Türkmen</span>
              </motion.h1>

              <motion.p
                className="text-xl lg:text-2xl text-slate-300 mb-8"
                initial={{ opacity: 0 }}
                animate={heroInView ? { opacity: 1 } : {}}
                transition={{ delay: 0.4 }}
              >
                {t.hero.role}
                <br />
                <span className="text-amber-400">{t.hero.university}</span>
              </motion.p>

              <motion.div
                className="flex flex-wrap gap-4 justify-center lg:justify-start mb-8"
                initial={{ opacity: 0 }}
                animate={heroInView ? { opacity: 1 } : {}}
                transition={{ delay: 0.5 }}
              >
                <button
                  onClick={() => document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })}
                  className="btn-primary"
                >
                  <Mail className="w-5 h-5" />
                  {t.hero.cta1}
                </button>

                <button
                  onClick={handleDownloadCV}
                  className="btn-secondary"
                >
                  <Download className="w-5 h-5" />
                  {t.hero.cta2}
                </button>
              </motion.div>

              <motion.div
                className="flex gap-4 justify-center lg:justify-start"
                initial={{ opacity: 0 }}
                animate={heroInView ? { opacity: 1 } : {}}
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

            {/* Profile Image */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={heroInView ? { opacity: 1, scale: 1 } : {}}
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
      </section>

      {/* About Section */}
      <section
        ref={aboutRef}
        className="section-padding bg-slate-900/50"
      >
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={aboutInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="section-header"
          >
            <h2 className="section-title gradient-text">{t.about.title}</h2>
            <p className="section-subtitle">{t.about.subtitle}</p>
          </motion.div>

          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={aboutInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="space-y-6 text-lg text-slate-300 leading-relaxed"
            >
              <p>{t.about.p1}</p>
              <p>{t.about.p2}</p>
              <p>{t.about.p3}</p>
              <p>{t.about.p4}</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Skills Section */}
      <section
        ref={skillsRef}
        className="section-padding"
      >
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={skillsInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="section-header"
          >
            <h2 className="section-title gradient-text">{t.skills.title}</h2>
            <p className="section-subtitle">{t.skills.subtitle}</p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">

            {/* Frontend */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={skillsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="card"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-amber-500/20 to-orange-500/20 flex items-center justify-center">
                  <Code2 className="w-6 h-6 text-amber-400" />
                </div>
                <h3 className="text-xl font-bold">{t.skills.frontend}</h3>
              </div>

              <div className="flex flex-wrap gap-2">
                {skills.frontend.map((skill, idx) => (
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
              animate={skillsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="card"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-orange-500/20 to-pink-500/20 flex items-center justify-center">
                  <Database className="w-6 h-6 text-orange-400" />
                </div>
                <h3 className="text-xl font-bold">{t.skills.backend}</h3>
              </div>

              <div className="flex flex-wrap gap-2">
                {skills.backend.map((skill, idx) => (
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
              animate={skillsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="card"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-pink-500/20 to-purple-500/20 flex items-center justify-center">
                  <Wrench className="w-6 h-6 text-pink-400" />
                </div>
                <h3 className="text-xl font-bold">{t.skills.tools}</h3>
              </div>

              <div className="flex flex-wrap gap-2">
                {skills.tools.map((skill, idx) => (
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

      {/* Projects Section */}
      <section
        ref={projectsRef}
        className="section-padding bg-slate-900/50"
      >
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={projectsInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="section-header"
          >
            <h2 className="section-title gradient-text">{t.projects.title}</h2>
            <p className="section-subtitle">{t.projects.subtitle}</p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {projects.map((project, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                animate={projectsInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: idx * 0.1 }}
                className="card group"
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
                <h3 className="text-xl font-bold mb-3 text-white">{project.title}</h3>
                <p className="text-slate-400 mb-4 leading-relaxed">{project.description}</p>

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
                    className="flex items-center gap-2 text-sm text-slate-300 hover:text-amber-400 transition-colors"
                  >
                    <Github className="w-4 h-4" />
                    {t.projects.code}
                  </a>
                  <a
                    href={project.demo}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-slate-300 hover:text-orange-400 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    {t.projects.demo}
                  </a>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section
        id="contact"
        ref={contactRef}
        className="section-padding"
      >
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={contactInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="section-header"
          >
            <h2 className="section-title gradient-text">{t.contact.title}</h2>
            <p className="section-subtitle">{t.contact.subtitle}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={contactInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="max-w-2xl mx-auto"
          >
            <form onSubmit={handleSubmit} className="space-y-6">

              <div>
                <label htmlFor="name" className="block text-sm font-medium text-slate-300 mb-2">
                  {t.contact.name}
                </label>
                <input
                  type="text"
                  id="name"
                  required
                  className="input-field"
                  placeholder={t.contact.namePlaceholder}
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
                  {t.contact.email}
                </label>
                <input
                  type="email"
                  id="email"
                  required
                  className="input-field"
                  placeholder={t.contact.emailPlaceholder}
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>

              <div>
                <label htmlFor="message" className="block text-sm font-medium text-slate-300 mb-2">
                  {t.contact.message}
                </label>
                <textarea
                  id="message"
                  rows={5}
                  required
                  className="input-field resize-none"
                  placeholder={t.contact.messagePlaceholder}
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                />
              </div>

              <button type="submit" className="btn-primary w-full justify-center">
                <Send className="w-5 h-5" />
                {t.contact.send}
              </button>

            </form>

            {/* Contact Info */}
            <div className="mt-12 text-center">
              <p className="text-slate-400 mb-4">{t.contact.or}</p>
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

      {/* Footer */}
      <footer className="py-8 bg-slate-950/50 border-t border-slate-800">
        <div className="container-custom">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-slate-400">
              {t.contact.footer}
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

    </div>
  );
}

export default App;