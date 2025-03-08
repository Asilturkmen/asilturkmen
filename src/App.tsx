import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Github, Instagram, Linkedin, Mail, Send } from 'lucide-react';
import profilePic from './img/profile.png';


function App() {
  const [heroRef, heroInView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  const [aboutRef, aboutInView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  const [contactRef, contactInView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // "mailto" linkini oluştur
    const mailtoLink = `mailto:turkmenasil@hotmail.com?subject=Contact from ${formData.name}&body=Name: ${formData.name}%0D%0AEmail: ${formData.email}%0D%0AMessage: ${formData.message}`;

    // Kullanıcıyı mail istemcisine yönlendir
    window.location.href = mailtoLink;
};

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 via-blue-900 to-cyan-900 text-white">
      {/* Hero Section */}
      <motion.section
        ref={heroRef}
        initial={{ opacity: 0 }}
        animate={heroInView ? { opacity: 1 } : {}}
        className="min-h-screen relative overflow-hidden flex items-center justify-center"
      >
        {/* Animated particles background */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(50)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-blue-400 rounded-full"
              initial={{
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                scale: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.2,
              }}
              animate={{
                y: [null, Math.random() * -500],
                opacity: [null, 0],
              }}
              transition={{
                duration: Math.random() * 10 + 10,
                repeat: Infinity,
                ease: "linear",
              }}
            />
          ))}
        </div>

        {/* Main content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-12">
            {/* Left side - Text content */}
            <motion.div
              className="flex-1 text-center lg:text-left"
              initial={{ x: -100, opacity: 0 }}
              animate={heroInView ? { x: 0, opacity: 1 } : {}}
              transition={{ duration: 1, delay: 0.2 }}
            >
              <motion.h2
                className="text-xl text-cyan-400 mb-4 font-medium"
                initial={{ y: 20, opacity: 0 }}
                animate={heroInView ? { y: 0, opacity: 1 } : {}}
                transition={{ duration: 0.8 }}
              >
                Hi, I am
              </motion.h2>
              <motion.h1
                className="text-5xl lg:text-7xl font-bold mb-6"
                initial={{ y: 20, opacity: 0 }}
                animate={heroInView ? { y: 0, opacity: 1 } : {}}
                transition={{ duration: 0.8, delay: 0.3 }}
              >
                <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-400 text-transparent bg-clip-text">
                  Asil Türkmen
                </span>
              </motion.h1>
              <motion.p
                className="text-2xl lg:text-3xl text-blue-200 mb-8"
                initial={{ y: 20, opacity: 0 }}
                animate={heroInView ? { y: 0, opacity: 1 } : {}}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                Software Engineering Student at
                <br />
                <span className="text-cyan-300">Eastern Mediterranean University</span>
              </motion.p>
              <motion.div
                className="flex justify-center lg:justify-start space-x-6"
                initial={{ y: 20, opacity: 0 }}
                animate={heroInView ? { y: 0, opacity: 1 } : {}}
                transition={{ duration: 0.8, delay: 0.5 }}
              >
                <motion.a
                  href="https://github.com/Sonasil"
                  className="p-3 bg-blue-900/30 rounded-full hover:bg-blue-800/50 transition-all duration-300"
                  whileHover={{ y: -5, scale: 1.1 }}
                >
                  <Github className="w-7 h-7 text-cyan-300" />
                </motion.a>
                <motion.a
                  href="https://www.linkedin.com/in/asil-t%C3%BCrkmen-224ab0241/"
                  className="p-3 bg-blue-900/30 rounded-full hover:bg-blue-800/50 transition-all duration-300"
                  whileHover={{ y: -5, scale: 1.1 }}
                >
                  <Linkedin className="w-7 h-7 text-cyan-300" />
                </motion.a>
                <motion.a
                  href="https://www.instagram.com/asil_turkmen28/"
                  className="p-3 bg-blue-900/30 rounded-full hover:bg-blue-800/50 transition-all duration-300"
                  whileHover={{ y: -5, scale: 1.1 }}
                >
                  <Instagram className="w-7 h-7 text-cyan-300" />
                </motion.a>
              </motion.div>
            </motion.div>

            {/* Right side - Profile image */}
            <motion.div
              className="flex-1 relative"
              initial={{ x: 100, opacity: 0 }}
              animate={heroInView ? { x: 0, opacity: 1 } : {}}
              transition={{ duration: 1, delay: 0.4 }}
            >
              <div className="relative w-64 h-64 lg:w-96 lg:h-96 mx-auto">
                <motion.div
                  className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 via-cyan-400 to-blue-500"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.5, 0.8, 0.5],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    repeatType: "reverse",
                  }}
                  style={{ filter: 'blur(20px)' }}
                />
                <img
                  src={profilePic} 
                  alt="Profil Resmi"
                  className=" rounded-full relative z-10"
                />
              </div>
            </motion.div>
          </div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, y: [0, 10, 0] }}
          transition={{
            duration: 2,
            delay: 2,
            repeat: Infinity,
            repeatType: "reverse",
          }}
        >
          <div className="w-6 h-10 border-2 border-cyan-300 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-cyan-300 rounded-full mt-2 animate-bounce" />
          </div>
        </motion.div>
      </motion.section>

      {/* About Section */}
      <motion.section
        ref={aboutRef}
        className="py-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden"
        initial={{ opacity: 0, y: 50 }}
        animate={aboutInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.8 }}
      >
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-16 bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-400 text-transparent bg-clip-text">
            About
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              className="relative"
              initial={{ x: -50, opacity: 0 }}
              animate={aboutInView ? { x: 0, opacity: 1 } : {}}
              transition={{ delay: 0.2 }}
            >
              <div className="aspect-square rounded-2xl overflow-hidden">
                <img
                  src="https://images.unsplash.com/photo-1571171637578-41bc2dd41cd2?auto=format&fit=crop&q=80&w=800"
                  alt="Programming"
                  className="w-full h-full object-cover"
                />
              </div>
            </motion.div>
            <motion.div
              className="space-y-6"
              initial={{ x: 50, opacity: 0 }}
              animate={aboutInView ? { x: 0, opacity: 1 } : {}}
              transition={{ delay: 0.4 }}
            >
              <p className="text-xl text-blue-200">
              Hello! I'm Asil, a Software Engineering student at Eastern Mediterranean University. I am passionate about modern web technologies and software development.
              </p>
              <p className="text-xl text-blue-200">
              I am gaining experience in frontend and backend technologies and constantly trying to improve myself.
              </p>
              <p className="text-xl text-blue-200">
              With my passion for learning and problem solving skills, I aim to develop user-friendly and innovative web applications.
              </p>
              <div className="pt-6">
              <motion.button
  className="px-8 py-3 bg-gradient-to-r from-blue-500 via-cyan-500 to-blue-500 rounded-full text-white font-medium hover:opacity-90 transition-all"
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  onClick={() => {
    const link = document.createElement('a');
    link.href = '/Englishcv.pdf'; // Public içindeki dosya
    link.download = 'Englishcv.pdf'; // Dosyayı bilgisayara indirir
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }}
>
  DOWNLOAD MY CV
</motion.button>

              </div>
            </motion.div>
          </div>
        </div>
      </motion.section>

      {/* Contact Section */}
      <motion.section
        ref={contactRef}
        className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-950/80 to-cyan-900/80 backdrop-blur-sm"
        initial={{ opacity: 0, y: 50 }}
        animate={contactInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.8 }}
      >
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-16 bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-400 text-transparent bg-clip-text">
            contact
          </h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={contactInView ? { opacity: 1, x: 0 } : {}}
              transition={{ delay: 0.2 }}
            >
              <label htmlFor="name" className="block text-sm font-medium text-cyan-200 mb-2">
                Name
              </label>
              <input
                type="text"
                id="name"
                className="w-full px-4 py-3 rounded-lg bg-blue-900/30 border border-blue-700/50 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                placeholder="Your Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={contactInView ? { opacity: 1, x: 0 } : {}}
              transition={{ delay: 0.3 }}
            >
              <label htmlFor="email" className="block text-sm font-medium text-cyan-200 mb-2">
              Email
              </label>
              <input
                type="email"
                id="email"
                className="w-full px-4 py-3 rounded-lg bg-blue-900/30 border border-blue-700/50 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                placeholder="Emailexamlpe@gmail.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={contactInView ? { opacity: 1, x: 0 } : {}}
              transition={{ delay: 0.4 }}
            >
              <label htmlFor="message" className="block text-sm font-medium text-cyan-200 mb-2">
                Message
              </label>
              <textarea
                id="message"
                rows={4}
                className="w-full px-4 py-3 rounded-lg bg-blue-900/30 border border-blue-700/50 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                placeholder="Your message..."
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              />
            </motion.div>
            <motion.button
              type="submit"
              className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 via-cyan-500 to-blue-500 text-white font-medium rounded-lg hover:opacity-90 transition-all flex items-center justify-center space-x-2 group"
              initial={{ opacity: 0, y: 20 }}
              animate={contactInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.5 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <span>Send</span>
              <Send className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </motion.button>
          </form>
        </div>
      </motion.section>

      {/* Footer */}
      <footer className="py-8 text-center text-blue-300 bg-blue-950/50">
        <p>© 2024 Asil Türkmen. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;