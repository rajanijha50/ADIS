import {
  User,
  Moon,
  Bell,
  Camera,
  Phone,
  Mail,
  Link2,
  Twitter,
  Github,
  Linkedin,
  FileEdit,
  Trash2,
  DatabaseZap,
  Settings2,
  AudioLines,
} from "lucide-react";
import React, { useState, useEffect } from "react";
import { SendNotification } from "../SendNotification";

import { useSelector } from "react-redux";
import { RootState } from "../../app/store";
export default function GeneralSettings() {
  const { user } = useSelector((state: RootState) => state.user);
  console.log("user in settings: ", user)

  const [animationsEnabled, setAnimationsEnabled] = useState(() => {
    const saved = localStorage.getItem("app-animations");
    return saved !== null ? JSON.parse(saved) : true;
  });

  const [darkThemeEnabled, setDarkThemeEnabled] = useState(() => {
    const saved = localStorage.getItem("app-dark-theme");
    return saved !== null ? JSON.parse(saved) : true;
  });

  const [notificationsEnabled, setNotificationsEnabled] = useState(() => {
    const saved = localStorage.getItem("app-notifications");
    return saved !== null ? JSON.parse(saved) : true;
  });

  const [fullName, setFullName] = useState(user?.full_name || "");
  // const [user?.email, setEmail] = useState(user?.user?.email || "");
  const [phoneNumber, setPhoneNumber] = useState(user?.contact || "");
  const [avatar, setAvatar] = useState<string | null>(user?.profile_pic || "");
  const [twitterURL, setTwitterURL] = useState("");
  const [githubURL, setGithubURL] = useState("");
  const [linkedinURL, setLinkedInURL] = useState("");

  useEffect(() => {
    localStorage.setItem("app-animations", JSON.stringify(animationsEnabled));
    if (animationsEnabled) {
      document.documentElement.classList.remove("no-animations");
    } else {
      document.documentElement.classList.add("no-animations");
    }
  }, [animationsEnabled]);

  function handleImageUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      setAvatar(URL.createObjectURL(file));
      console.log(URL.createObjectURL(file));
      console.log(file);
    }
  }

  async function handleUpdateProfile () {
    // SendNotification('message saved successfully!', 'default')
    if (!fullName || !user?.email || !phoneNumber) {
      SendNotification("Please fill the requied fields", "error");
      return;
    }

    if (!user?.email.includes("@") || !user?.email.includes(".")) {
      SendNotification("Please enter a valid user?.email", "error");
      return;
    }

    if (!phoneNumber.match(/^[0-9]+$/) || phoneNumber.length !== 10) {
      SendNotification("Please enter a valid phone number", "error");
      return;
    }

    try{
      const response = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/user/profile`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: user?.email,
        name: fullName,
        contact: phoneNumber
      }),
    });

    const data = await response.json();
    console.log(data)
    
    } catch (error) {
      console.log(error);
    }
  }

  function handleExportJSON() {
    SendNotification("Data exported successfully!", "success");
  }

  function handleClearConversation() {
    SendNotification("Data cleared successfully!", "success");
  }

  function handleDeleteAccount() {
    SendNotification("Account deleted successfully!", "error");
  }

  return (
    <div className="space-y-8 animate-fade-in-up">
      <div className="border-b border-border-divider pb-6">
        <h2 className="text-3xl font-bold tracking-tight text-primary">
          General Settings
        </h2>
        <p className="text-secondary mt-2 text-sm">
          Manage your account settings and preferences.
        </p>
      </div>

      <div className="space-y-6">
        {/* Profile Section */}
        <section className="bg-card border border-border-card rounded-2xl p-6 shadow-card hover:border-border-card-hover transition-colors">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-500/20">
                <User size={24} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-primary">
                  Profile Information
                </h3>
                <p className="text-text-muted text-sm">
                  Update your personal identity
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-10">
            {/* Avatar Upload */}
            <div className="flex flex-col items-center gap-4">
              <div className="relative group">
                {avatar ? (
                  <img
                    src={avatar}
                    alt="Preview"
                    className="w-32 h-32 rounded-full border-2 border-dashed border-border-divider flex items-center justify-center bg-input overflow-hidden group-hover:border-accent-primary transition-all"
                  />
                ) : (
                  <>
                    <div className="hidden w-32 h-32 rounded-full border-2 border-dashed border-border-divider items-center justify-center bg-input overflow-hidden group-hover:border-accent-primary transition-all">
                      <User
                        size={48}
                        className="text-placeholder group-hover:scale-110 transition-transform"
                      />
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity cursor-pointer">
                        <Camera size={24} className="text-white" />
                      </div>
                    </div>
                    <button className="absolute -bottom-1 -right-1 p-2 bg-accent-primary text-white rounded-full shadow-lg hover:scale-110 transition-transform cursor-pointer">
                      <Camera size={14} />
                    </button>

                    <input
                      type="file"
                      onChange={handleImageUpload}
                      accept="image/*"
                      name="ImageSelector"
                      id="ImageSelector"
                      className="opacity-0 w-full h-full cursor-pointer absolute top-0 left-0 z-10 rounded-full"
                    />
                  </>
                )}
              </div>

              {avatar && (
                <div className="hidden w-32 justify-around items-center">
                  <button
                    title="Edit"
                    className="relative p-2 rounded-md hover:bg-input-hover text-primary hover:text-accent-primary transition-colors"
                    onClick={() => {
                      setAvatar(null);
                      setTimeout(() => {
                        document.getElementById("ImageSelector")?.click();
                      }, 100);
                    }}
                  >
                    {/* <input type="file" name="" id="" /> */}
                    <FileEdit size={20} />
                  </button>
                  <button
                    onClick={() => setAvatar(null)}
                    title="Remove"
                    className="p-2 rounded-md hover:bg-red-500/10 text-red-500 transition-colors"
                  >
                    <Trash2 size={20} />
                  </button>
                </div>
              )}
            </div>

            {/* Form Fields */}
            <div className="flex-1 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-1 gap-4">
                <div className="space-y-2 w-fit flex flex-col">
                  <label className="text-sm font-medium text-text-secondary">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Tony Stark"
                    className="w-72 bg-input border border-border-input rounded-lg px-4 py-2.5 text-primary placeholder-placeholder focus:outline-none focus:border-border-input-focus focus:ring-1 focus:ring-focus-glow transition-all"
                  />
                </div>
                <div className="space-y-2 w-fit flex flex-col">
                  <label className="text-sm font-medium text-text-secondary flex items-center gap-2">
                    <Mail size={14} /> Email Address
                  </label>
                  <input
                    type="user?.email"
                    value={user?.email}
                    // disabled
                    onChange={() => {
                      SendNotification("Email change not allowed", "error");
                    }}
                    placeholder="tony@starkindustries.com"
                    className="w-72 bg-input border border-border-input rounded-lg px-4 py-2.5 text-primary placeholder-placeholder focus:outline-none focus:border-border-input-focus focus:ring-1 focus:ring-focus-glow transition-all"
                  />
                </div>
                <div className="space-y-2 w-fit">
                  <label className="text-sm font-medium text-text-secondary flex items-center gap-2">
                    <Phone size={14} /> Contact Number
                  </label>
                  <input
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    placeholder="1234567890"
                    className="w-full bg-input border border-border-input rounded-lg px-4 py-2.5 text-primary placeholder-placeholder focus:outline-none focus:border-border-input-focus focus:ring-1 focus:ring-focus-glow transition-all"
                  />
                </div>
              </div>

              {/* Social Links */}
              <div className="hidden space-y-3 pt-2">
                <label className="text-sm font-medium text-text-secondary flex items-center gap-2">
                  <Link2 size={14} /> Social Profiles
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="relative">
                    <Twitter
                      size={14}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary"
                    />
                    <input
                      type="text"
                      value={twitterURL}
                      onChange={(e) => setTwitterURL(e.target.value)}
                      placeholder="Twitter URL"
                      className="w-full bg-input border border-border-input rounded-lg pl-9 pr-3 py-2 text-xs text-primary placeholder-placeholder focus:outline-none focus:border-border-input-focus transition-all"
                    />
                  </div>
                  <div className="relative">
                    <Linkedin
                      size={14}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary"
                    />
                    <input
                      type="text"
                      value={linkedinURL}
                      onChange={(e) => setLinkedInURL(e.target.value)}
                      placeholder="LinkedIn URL"
                      className="w-full bg-input border border-border-input rounded-lg pl-9 pr-3 py-2 text-xs text-primary placeholder-placeholder focus:outline-none focus:border-border-input-focus transition-all"
                    />
                  </div>
                  <div className="relative">
                    <Github
                      size={14}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary"
                    />
                    <input
                      type="text"
                      value={githubURL}
                      onChange={(e) => setGithubURL(e.target.value)}
                      placeholder="GitHub URL"
                      className="w-full bg-input border border-border-input rounded-lg pl-9 pr-3 py-2 text-xs text-primary placeholder-muted focus:outline-none focus:border-border-input-focus transition-all"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 flex justify-end">
            <button
              onClick={handleUpdateProfile}
              className="px-5 py-2.5 bg-accent-primary hover:bg-accent-secondary text-white font-medium rounded-lg transition-colors shadow-glow active:scale-95"
            >
              Update Profile
            </button>
          </div>
        </section>

        {/* Data Management Section */}
        <section className="hidden bg-card border border-border-card rounded-2xl p-6 shadow-card hover:border-border-card-hover transition-colors">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-red-500/10 text-red-400 rounded-xl border border-red-500/20">
              <DatabaseZap size={24} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary">
                Data Management
              </h3>
              <p className="text-text-muted text-sm">
                Manage your chat history and data
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-xl bg-input border border-border-input hover:border-border-input-focus transition-colors">
              <div>
                <h4 className="text-primary font-medium">
                  Export Chat History
                </h4>
                <p className="text-xs text-text-muted mt-0.5">
                  Download your data in JSON format
                </p>
              </div>
              <button
                onClick={() => handleExportJSON()}
                className="px-4 py-2 bg-accent-primary/10 hover:bg-accent-primary/20 text-accent-primary text-xs font-semibold rounded-lg border border-accent-primary/20 transition-colors"
              >
                Export JSON
              </button>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-input border border-border-input hover:border-border-input-focus transition-colors">
              <div>
                <h4 className="text-primary font-medium">
                  Clear All Conversations
                </h4>
                <p className="text-xs text-text-muted mt-0.5">
                  Delete all your conversations
                </p>
              </div>
              <button
                onClick={() => handleClearConversation()}
                className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-semibold rounded-lg border border-red-500/20 transition-colors"
              >
                Clear Data
              </button>
            </div>
            <div className="flex items-center justify-between p-4 rounded-xl bg-input border border-border-input hover:border-border-input-focus transition-colors">
              <div>
                <h4 className="text-primary font-medium">Delete Account</h4>
                <p className="text-xs text-text-muted mt-0.5">
                  Delete your account and all your data
                </p>
              </div>
              <button
                onClick={() => handleDeleteAccount()}
                className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-semibold rounded-lg border border-red-500/20 transition-colors"
              >
                Delete Account
              </button>
            </div>
          </div>
        </section>

        {/* Preferences Section */}
        <section className="hidden bg-card border border-border-card rounded-2xl p-6 shadow-card hover:border-border-card-hover transition-colors">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-purple-500/10 text-purple-400 rounded-xl border border-purple-500/20">
              <Settings2 size={24} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary">
                Preferences
              </h3>
              <p className="text-text-muted text-sm">
                Customize your experience
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-xl bg-input border border-border-input hover:border-border-input-focus transition-colors">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-[#ffffff0a] rounded-lg text-secondary">
                  <Moon size={20} />
                </div>
                <div>
                  <h4 className="text-primary font-medium">Dark Mode</h4>
                  <p className="text-xs text-text-muted mt-0.5">
                    Toggle dark mode appearance
                  </p>
                </div>
              </div>
              <div
                onClick={() => setDarkThemeEnabled(!darkThemeEnabled)}
                className={`relative inline-block w-12 h-6 rounded-full transition-colors cursor-pointer ${darkThemeEnabled ? "bg-accent-primary shadow-glow" : "bg-[#454853]"}`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm ${darkThemeEnabled ? "left-[26px]" : "left-1"}`}
                ></span>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-input border border-border-input hover:border-border-input-focus transition-colors">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-[#ffffff0a] rounded-lg text-secondary">
                  <AudioLines size={20} />
                </div>
                <div>
                  <h4 className="text-primary font-medium">
                    App Icon Animation
                  </h4>
                  <p className="text-xs text-text-muted mt-0.5">
                    Toggle app icon animation
                  </p>
                </div>
              </div>
              <div
                onClick={() => setAnimationsEnabled(!animationsEnabled)}
                className={`relative inline-block w-12 h-6 rounded-full transition-colors cursor-pointer ${animationsEnabled ? "bg-accent-primary shadow-glow" : "bg-[#454853]"}`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm ${animationsEnabled ? "left-[26px]" : "left-1"}`}
                ></span>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-input border border-border-input hover:border-border-input-focus transition-colors">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-[#ffffff0a] rounded-lg text-secondary">
                  <Bell size={20} />
                </div>
                <div>
                  <h4 className="text-primary font-medium">Notifications</h4>
                  <p className="text-xs text-text-muted mt-0.5">
                    Enable push notifications
                  </p>
                </div>
              </div>
              <div
                onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                className={`relative inline-block w-12 h-6 rounded-full transition-colors cursor-pointer ${notificationsEnabled ? "bg-accent-primary shadow-glow" : "bg-[#454853]"}`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm ${notificationsEnabled ? "left-[26px]" : "left-1"}`}
                ></span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
