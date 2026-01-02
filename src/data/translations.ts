export type Language = 'tr' | 'en';

export const translations = {
    tr: {
        hero: {
            greeting: 'Merhaba, Ben',
            role: 'Yazılım Mühendisliği Öğrencisi',
            university: 'Doğu Akdeniz Üniversitesi',
            cta1: 'İletişime Geç',
            cta2: 'CV İncele'
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
            visit: 'Ziyaret Et'
        },
        contact: {
            title: 'İletişime Geçin',
            subtitle: 'Birlikte çalışalım',
            name: 'İsim',
            email: 'E-posta',
            message: 'Mesaj',
            send: 'Mesaj Gönder',
            sending: 'Gönderiliyor...',
            namePlaceholder: 'Adınız',
            emailPlaceholder: 'ornek@email.com',
            messagePlaceholder: 'Mesajınız...',
            or: 'Veya doğrudan bana ulaşın:',
            footer: '© 2026 Asil Türkmen. Tüm hakları saklıdır.',
            success: '✅ Mesajınız başarıyla gönderildi!',
            error: '❌ Mesaj gönderilemedi. Lütfen tekrar deneyin.',
            generalError: '❌ Bir hata oluştu. Lütfen tekrar deneyin.'
        }
    },
    en: {
        hero: {
            greeting: 'Hi, I am',
            role: 'Software Engineering Student',
            university: 'Eastern Mediterranean University',
            cta1: 'Get In Touch',
            cta2: 'View CV'
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
            visit: 'Visit'
        },
        contact: {
            title: 'Get In Touch',
            subtitle: 'Let\'s work together',
            name: 'Name',
            email: 'Email',
            message: 'Message',
            send: 'Send Message',
            sending: 'Sending...',
            namePlaceholder: 'Your Name',
            emailPlaceholder: 'your.email@example.com',
            messagePlaceholder: 'Your message...',
            or: 'Or reach me directly at:',
            footer: '© 2026 Asil Türkmen. All rights reserved.',
            success: '✅ Message sent successfully!',
            error: '❌ Failed to send message. Please try again.',
            generalError: '❌ An error occurred. Please try again.'
        }
    }
};
