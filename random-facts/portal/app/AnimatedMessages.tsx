import { AIContentState, getFunFacts } from "@/app/actions";
import Image from "next/image";
import { startTransition, useActionState, useEffect } from "react";
import { motion } from "motion/react";

const initialState: AIContentState = {
  funFacts: [],
  error: null,
};

const cardPositions = [
  {
    top: "5%",
    left: "5%",
  },
  {
    top: "30%",
    right: "5%",
  },
  {
    bottom: "5%",
    left: "5%",
  },
];

export default function AnimatedMessages() {
  const [state, dispatch] = useActionState(getFunFacts, initialState);

  useEffect(() => {
    startTransition(() => {
      dispatch(3);
    });
  }, []);

  return (
    <div className="w-full h-full absolute">
      {state.funFacts.map(({ fact }, index) => (
        <div
          key={index}
          style={{
            position: "absolute",
            transform: `rotate(${Math.random() * 20 - 10}deg)`,
            ...cardPositions[index % 3],
          }}
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            transition={{ duration: 0.5 }}
            whileHover={{
              scale: 1.25,
              rotate: [0, 10, -10, 0],
              transition: { duration: 0.5 },
            }}
            className="w-80 h-80 bg-white shadow-lg rounded-lg overflow-hidden border-slate-700 pointer-events-auto"
          >
            <div className="h-1/2 bg-white">
              {state.funFacts[index].imgSrc && (
                <Image
                  src={state.funFacts[index].imgSrc}
                  alt="Random"
                  className="w-full h-full object-cover"
                  width={320}
                  height={160}
                />
              )}
            </div>
            <div className="h-1/2 p-4 flex items-center justify-center">
              <p className="text-center text-sm text-black">{fact}</p>
            </div>
          </motion.div>
        </div>
      ))}
    </div>
  );
}
